Demonstration of a Google App Engine site with Duo authentication.

Developed with the Google App Engine SDK 1.4.1.

# Install/Run

To set up, edit duo.conf.  Edit the application name in app.yaml if you want
to deploy to GAE.

To run the demo server locally from one directory up:

    dev_appserver.py appengine

To deploy to GAE from one directory up:

    appcfg.py update appengine

# Usage

Visit the root URL, then authenticate with a user with an email address
with a duosecurity.com domain and a local component which matches the
username on your Duo server.

# Todo

UI to remove the Duo loggedin cookie would be nice.  Remove the 'logged_in'
cookie to require Duo authentication.

A username without an @ in it will error.

