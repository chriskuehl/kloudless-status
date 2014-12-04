# Kloudless Status Dashboard

This app powers the [Kloudless Status Dashboard][http://status.kloudless.com].

# Publishing statuses

To update the status, post a tweet of the format:

    ${SERVICE}-${STATUS}: ${COMMENT}

where SERVICE is one of {API,JS,DASH}, STATUS is one of {UP,DOWN,ISSUE}, and
COMMENT is some free-form description.

Examples:

* API-DOWN: everything is on fire
* API-UP: it's back now
* JS-NOTICE: someone deleted the javascript
* DASH-DOWN: helpppp meeee

## Development setup

1. Download the [Google App Engine
   SDK](https://cloud.google.com/appengine/downloads) (for Python)
2. Extract it somewhere (Linux) or run the installer (OS X).
3. From the root of this repo, run:

       dev_appserver.py --host 0.0.0.0 --admin_host 0.0.0.0 \
           --clear_datastore 1 situation/

   **Note:** `dev_appserver.py` is an executable that comes from the App Engine
   SDK. It might not be on your PATH, so adjust as necessary.

   This will launch the app at [localhost:8080](http://localhost:8080/) and a
   mock appserver console at [localhost:8000](http://localhost:8000/).

   If you want cron jobs to run (e.g. to fetch twitter messages or calculate
   uptime), you will need to trigger them manually from the appserver console
   (in development mode, they don't run automatically).

Changes you make to any file should take effect immediately. If you want to
clear the datastores, just quit (`^C`) and re-start the app.

## Deploying to Google App Engine

To deploy to Google App Engine, you need your Google Apps account to have
"Developer" permissions to the app.

## Setting up OAuth2 authentication

Instead of using password auth (which is complicated if you use 2FA), you
should set up OAuth2 with the App Engine SDK.

From the root of this git repo, run

    appcfg.py --oauth2 list_versions situation/

...to configure OAuth2. (`list_versions` is just a harmless command, rather
than e.g. trying to deploy). It will launch a web browser and prompt you to
grant permission.

(If you're using e.g. vagrant for development, it might do something crazy like
try to launch lynx to authorize the token, which will fail since it doesn't
support JavaScript. You can pass `--noauth_local_webserver` and follow the
instructions instead.)

## Deploying

Deploying is really easy once OAuth2 is ready. From the root of this repo:

    appcfg.py --oauth2 update situation/

You might see a bunch of warnings about mimetypes, but you can probably just
ignore them?

Deploying takes ~15 seconds, and will update the live site immediately. The app
is available at:

* [status.kloudless.com](http://status.kloudless.com/)
* [kloudless-status-2.appspot.com](http://kloudless-status-2.appspot.com)
