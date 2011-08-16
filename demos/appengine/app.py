"""
Demonstration of Duo authentication on Google App Engine.
To use, edit duo.conf, set gae_domain to an appropriate email domain,
and visit /.
"""

import ConfigParser
import logging

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import duo_web
import cookie

configfile = 'duo.conf'
cookie_secret = 'gidOKaKcT6SGndun6pzQaM/opQOdDU3XiMFMAX2FE7A='

# Mutable globals, used because GAE will recycle them if the app is
# already running.  These should only be written to from main().
_DEBUG = True
application = None
ikey = None
skey = None
akey = None
host = None
gae_domain = None


class BasePage(webapp.RequestHandler, cookie.RequestHandler):
    cookie_secret = cookie_secret

    def user_email_parts(self, user):
        """
        Return a (local, domain) tuple for user.
        """
        return user.email().split('@')
    
    def both_logged_in(self):
        """
        Return True if the user has been authenticated with both
        Google and Duo.
        """
        user = users.get_current_user()
        if user:
            (username, _) = self.user_email_parts(user)
            if self.get_secure_cookie('logged_in') == username:
                return True
        return False


class AuthenticatedPage(BasePage):
    def get(self):
        if not self.both_logged_in():
            self.response.out.write(
                'Log in as a user with a %s email to continue: '
                '<a href="%s">Login.</a>' %
                (gae_domain, 'primary_auth'))
            return
        self.response.out.write(
            'Logged in as %s. <a href="%s">Logout.</a>' %
            (users.get_current_user(), users.create_logout_url('/')))


class PrimaryAuthPage(BasePage):
    def get(self):
        user = users.get_current_user()
        if user:
            (_, domain) = self.user_email_parts(user)
            if domain == gae_domain:
                self.redirect('/secondary_auth')
                return
        self.redirect(users.create_login_url(self.request.uri))
        return
            

class SecondaryAuthPage(BasePage):
    def get(self):
        if self.both_logged_in():
            self.redirect('/')
            return
        user = users.get_current_user()
        if not user:
            self.redirect('/')
            return
        (username, _) = self.user_email_parts(user)
        sig_request = duo_web.sign_request(ikey, skey, akey, username)
        self.response.out.write(
            "<script src='/static/Duo-Web-v1.bundled.min.js'></script>"
            "<script>"
            "Duo.init({'host':'%(host)s', 'post_action':'%(post_action)s', "
            "'sig_request':'%(sig_request)s'});"
            "</script>"
            "<iframe height='100%%' width='100%%' id='duo_iframe' />"
            % {'host':host, 'post_action':self.request.uri,
               'sig_request':sig_request})
        
    def post(self):
        """
        If we have a sig_response argument containig a Duo auth cookie
        indicating that the current user has logged in to both Google and
        Duo with matching usernames, write a login cookie and redirect to /.
        Otherwise, indicate failure.
        """
        user = users.get_current_user()
        if not user:        
            self.redirect('/')
            return

        sig_response = self.request.get('sig_response', '')
        duo_user = duo_web.verify_response(ikey, skey, akey, sig_response)
        if duo_user is None:
            self.write('Did not authenticate.')
            return

        # Note that since the secure cookie is never unset, Duo auth is not
        # required again until it expires, even if Google auth is required.
        # We can provide redirects on the logout URLs which we present to
        # unset the cookie, but the user could find and use a Google logout URL
        # without these.
        self.set_secure_cookie('logged_in', duo_user)
        self.redirect('/')


def initialize_globals(config):
    """
    Initialize and set the WSGI application and other globals.
    """
    global application
    global ikey, skey, akey, host
    global gae_domain
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)-8s: %(message)s - %(pathname)s:%(lineno)d")
    logging.debug('start')
    if application is None:
        application = webapp.WSGIApplication(
            [('/primary_auth', PrimaryAuthPage),
             ('/secondary_auth', SecondaryAuthPage),
             ('/', AuthenticatedPage),],
            debug=_DEBUG)
    if ikey is None or skey is None or host is None or gae_domain is None:
        ikey = config['ikey']
        skey = config['skey']
        akey = config['akey']        
        host = config['host']
        gae_domain = config['gae_domain']
        
def main():
    config = ConfigParser.ConfigParser()
    config.read(configfile)
    c_d = dict(config.items('duo'))
    c_d.update(dict(config.items('app')))
    initialize_globals(c_d)
    run_wsgi_app(application)
    
if __name__ == '__main__':
    main()
