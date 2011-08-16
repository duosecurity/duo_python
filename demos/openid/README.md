OpenID identity provider for Google App Engine for use with identities
provided by Google accounts.  See CREDITS for credits.

# Requirements

Developed with the Google App Engine SDK 1.4.1.

Tests require WebTest, http://pythonpaste.org/webtest/, and Mox,
http://code.google.com/p/pymox/.

# Install/Run

Edit application name in app.yaml.

Put the relevant Duo ikey, skey, and host in duo.conf.

Run the demo server locally from one directory up:

    dev_appserver.py openid

Deploy to GAE from one directory up:

    appcfg.py update openid

# Usage

Visit the root page of the app and log in.  Use the displayed OpenID URL when
authenticating with an OpenID consumer.

# Test

To run unit tests, have . and the Google App Engine SDK in your path
(/usr/local/bin/google_appengine on my CentOS box), and:

    python test

If you're not running on a Linux variant, you'll probably have to edit the
GAE paths in test/setup.py first, see comment.

Note that when testing with the demo server, you must log in with a
domain-free username (that is, not an email address - 'user', not
'user@example.com').  This is an App Engine demo server limitation and is 
only required for the demo server, not for a deployed app.

# Credits

Based on http://appengine-openid-provider.googlecode.com, which is
based on http://openid-provider.appspot.com, ported to the JanRain
python-openid library version 2.1.1.  That library is included.

Unit tests use appenginetest, modified from
https://gist.github.com/186251 .

# Todo

Duo username is the same as Google user nickname.  This should be configurable
with some kind of map between usernames.

If user is logged in as different from claimed ID, user doesn't get to re-login
or get any helpful info, doesn't get redirected back to RP.

If the expected user is not logged in, user gets login page, but OpenID flow
doesn't continue.

Can't use https ID.
http://test-id.org/OP/RequireSsl.aspx

Permission is not asked before sending Simple Registration Extension
attrs.  Missing required attrs don't cause auth failure.  Many attrs
not supported.
http://test-id.org/OP/Sreg.aspx

This test might not be properly handled:
http://test-id.org/OP/DelegatedIdentifierSelect.aspx
