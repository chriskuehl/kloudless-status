from __future__ import unicode_literals
from datetime import datetime, timedelta
import logging

import tweepy

import models


LOGGER = logging.getLogger(__name__)

SERVICES = [
    'API', 'JS', 'DASH'
]

STATUSES = [
    '', 'UP', 'DOWN', 'ISSUE'
]


class TwitterStatusProcessor(object):
    SEPARATOR = ':'

    def __init__(self, **auth):
        if auth:
            self.auth = tweepy.OAuthHandler(auth['consumer_key'],
                                            auth['consumer_secret'])
            self.auth.set_access_token(auth['token'], auth['token_secret'])

            self.twitter = tweepy.API(
                self.auth,
                api_root='/1.1',
            )

    def _parse_tweet(self, message, created_at, tweet_id, tweet_id_str):
        spec, _, message = message.partition(self.SEPARATOR)
        if not spec:
            return

        spec = spec.split('-')
        service = spec[0]
        if len(spec) > 1:
            state = spec[1].upper()
        else:
            state = ''
        if service not in SERVICES or state not in STATUSES:
            return

        self._insert(service, created_at, message, state, tweet_id_str)

        self._set_last_updated(service, tweet_id)

    def _get_tw_key(self, service=None):
        if not service:
            service = '__general'
        return service + '-timestamp'

    def _set_last_updated(self, service=None, tweet_id=None):
        key = self._get_tw_key(service)
        kv = models.KV(k=key, value=str(tweet_id), key_name=key)
        kv.put()

    def _set_notified(self, tweet_id):
        results = models.Tweet.all()
        results.filter('tweet_id =', tweet_id)

        for tweet in results:
            if tweet:
                tweet.set_notified()

    def _get_last_updated(self, service=None):
        key = self._get_tw_key(service)
        return models.KV.get(key)

    def _insert(self, service, created_at, message, status, tweet_id):
        key = '{}-{}'.format(service, created_at)
        tw = models.Tweet.all().filter('key_name=', key).fetch(1)

        if not tw:
            tw = models.Tweet(
                service=service,
                created_at=created_at,
                message=message,
                status=status,
                key_name=key,
                tweet_id=tweet_id,
                notified=False
            )

            tw.put()

    def _get_tweets(self, min_date):
        filters = {}
        if min_date:
            filters['since_id'] = min_date.value

        return self.twitter.user_timeline(**filters)

    def run(self):
        last_check = self._get_last_updated()

        # get tweets where > last_updated
        tweets = self._get_tweets(last_check)

        for tweet in tweets:
            self._parse_tweet(tweet.text,
                              tweet.created_at,
                              tweet.id,
                              tweet.id_str)

        if tweets:
            max_id = max(tweet.id for tweet in tweets)
            self._set_last_updated(tweet_id=max_id)
            return max_id == last_check

        return False

    def get(self, service=None, count=10):
        tweets = models.Tweet.all().filter(
            'service = ', service
        ).order('-created_at').fetch(limit=count)
        return tweets

    def get_by_date(self, service, date):
        tweets = models.Tweet.all().filter(
            'service = ', service
        ).filter(
            'created_date =', date.strftime('%Y-%m-%d')
        ).order('-created_at')
        return tweets

    def get_by_dates(self, service, min_date, max_date):
        tweets = models.Tweet.all().filter(
            'service = ', service
        ).filter(
            'created_at <=', max_date
        ).filter(
            'created_at >', min_date
        )

        return tweets

    def get_last_message(self, service):
        tweets = models.Tweet.all().filter(
            'service = ', service
        ).order('-created_at').fetch(1)

        try:
            return tweets[0]
        except IndexError:
            return None

    def get_latest_state(self, service):
        tweets = models.Tweet.all().filter(
            'service = ', service
        ).order('-created_at')
        for tweet in tweets:
            if tweet.status:
                return tweet.status
        return None

    def get_uptime_month(self, service):
        """Find the uptime for a given month by calculating the number of
        seconds the service was down over the number of seconds in a month.

        We make the assumption that 35 days ago, the service was up. We then
        read all tweets since then, modifying the state and calculating
        downtime as we go.

        We start early in case the month starts with downtime. As long as all
        downtime lasts less than five days, we can make an accurate calculation
        for 30 days, which is all we care about.
        """
        DAYS_PER_MONTH = 30
        GRACE_PERIOD = timedelta(days=5) # in case month starts with downtime

        end = datetime.now()
        start = end - timedelta(days=DAYS_PER_MONTH)

        tweets = self.get_by_dates(service, start - GRACE_PERIOD, end) \
            .order('created_at')

        # read tweets, calculate downtime
        currently_up = True
        last_update = start
        total_downtime = timedelta()

        for tweet in tweets:
            if not tweet.status:
                continue

            now_up = tweet.status == 'UP'

            if now_up == currently_up:
                continue

            if now_up:
                # only add the downtime if the it happened after the start
                if tweet.created_at > last_update:
                    total_downtime += (tweet.created_at - last_update)
            else:
                last_update = tweet.created_at

            currently_up = now_up

        if not currently_up:
            total_downtime += (end - last_update)

        seconds = lambda dt: float(dt.seconds + (dt.days * 24 * 60 * 60))
        downtime = (seconds(total_downtime) / seconds(end - start))
        return (1 - downtime) * 100
