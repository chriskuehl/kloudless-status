# Notice:
# If you are running this in production environment, generate
# these for your app at https://dev.twitter.com/apps/new
TWITTER = {
    'AUTH': {
        'consumer_key': 'XXXX',
        'consumer_secret': 'XXXX',
        'token': 'XXXX',
        'token_secret': 'XXXX',
     }
}

# The e-mail address to send notifications from
EMAIL = {
    'sender': 'Kloudless Status <noreply@kloudless.com>'
}

DEBUG = True

# Currently DASHBOARD does not send out notifications
NOTIFY_SERVICES = ['API', 'JS']
