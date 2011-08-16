# Adapted from http://code.google.com/p/appengine-openid-provider/,
# copyrighted 2006 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
An OpenID Provider. Allows Google users to log into OpenID servers using
their Google Account.

Based on http://code.google.com/p/google-app-engine-samples/,
licensed under the Apache Software License 2.0.

Uses JanRain's Python OpenID library, version 2.2.1, licensed under the
Apache Software License 2.0:
  http://openidenabled.com/python-openid/
"""

import Cookie
import datetime
import ConfigParser
import logging
import pprint
import sys, os
import urllib, urlparse
import hashlib

from google.appengine.api import datastore
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from openid.server import server as OpenIDServer
from openid.extensions.sreg import SRegRequest, SRegResponse
import openid.message
import store

import duo_web

duo_conf = 'duo.conf'
# Mutable globals, used because GAE will recycle them if the app is
# already running.  These should only be written to from main().
oidserver = None                        # OpenID protocol server
application = None                      # WSGI app
ikey = None
skey = None
akey = None
host = None
_DEBUG = True # should stack traces etc. should be shown in the browser?


class Handler(webapp.RequestHandler):
    """A base handler class with a couple OpenID-specific utilities."""

    def arg_map(self, request):
        """
        Return a map of the first value for each URL and POST argument
        in request.
        """
        return dict([(arg, request.get(arg)) for arg in request.arguments()])

    def logins(self, user):
        """
        Return a sequence of recent logins for user.
        """
        if not user:
            return []
        query = datastore.Query('Login')
        query['user ='] = user
        query.Order(('time', datastore.Query.DESCENDING))
        return query.Get(10)

    def cookie_key(self, trust_root, identity_url):
        """
        Return a cookie key suitable for remembering a login for user with
        identity_url to trust_root.
        """
        return 'openid_remembered_%s' % hashlib.md5(
            '%s %s' % (trust_root, identity_url)).hexdigest()
    
    def has_cookie(self, request, trust_root, identity_url):
        """
        Return True if the environment has a cookie which we set to
        remember this user with this trust_root.
        """
        return request.cookies.get(
            self.cookie_key(trust_root, identity_url)) == 'yes'

    def set_cookie(self, response, trust_root, identity_url):
        """
        Set a cookie on response to remember this user with this trust_root
        with a 2 week expiration.
        """
        expires = (datetime.datetime.now() + datetime.timedelta(weeks=2)
                   ).strftime('%a, %d %b %Y %H:%M:%S +0000')
        self.response.headers.add_header(
            'Set-Cookie', '%s=yes; expires=%s' % (
            self.cookie_key(trust_root, identity_url), expires))

    def get_identity_url(self, user, request):
        """
        Return an OpenID identity URL for the current user, or None.
        """
        if user is None:
            return None
        (scheme, netloc, dummy, dummy, dummy, dummy) = urlparse.urlparse(
            request.uri)
        # If accepting https, we need to normalize, and probably want to use
        # the same http ID URL.  GAE seems to make this tricky.
        #if netloc.endswith(':443'):
        #    scheme = 'https'
        #    netloc = netloc[:-4]
        return '%s://%s/%s' % (scheme, netloc, user.nickname())

    def add_sreg_fields(self, oidresponse, user):
        """
        Add requested Simple Registration Extension fields to oidresponse
        and return it.
        """
        sreg_req = SRegRequest.fromOpenIDRequest(oidresponse.request)
        if sreg_req.wereFieldsRequested():
            logging.debug("respond: sreg_req:%s",
                          sreg_req.allRequestedFields())
            sreg_map = dict(
                ((key, val) for (key, val) in 
                 {'nickname':user.nickname(), 'email':user.email()}.items()
                 if key in sreg_req.allRequestedFields()))
            oidresponse.addExtension(
                SRegResponse.extractResponse(sreg_req, sreg_map))
        return oidresponse

    def verify_request(self, oid_request, request):
        """
        Raise ProtocolError if we shouldn't respond to this
        request.
        """
        logging.debug(request.scheme)
        if oid_request.message.getArg(
            openid.message.OPENID2_NS, 'session_type') == 'no-encryption':
            if request.scheme != 'https':
                raise OpenIDServer.ProtocolError(oid_request.message)

    def render_response(self, response):
        """
        Render an OpenId response to my response, or bail and render an HTML
        error message if we can't.
        """
        try:
            encoded_response = oidserver.encodeResponse(response)
        except OpenIDServer.EncodingError, exc:
            self.report_error(str(exc))            
            return
        for header, value in encoded_response.headers.items():
            self.response.headers[header] = str(value)
        if encoded_response.code in (301, 302):
            logging.debug('respond: redirecting to %s' %
                          self.response.headers['location'])
            self.redirect(self.response.headers['location'])
            return
        else:
            self.response.set_status(encoded_response.code)
        if encoded_response.body:
            logging.debug('respond: sending response body: %s' %
                          encoded_response.body)
            self.response.out.write(encoded_response.body)
        else:
            self.response.out.write('')

    def respond(self, oidresponse, user=None):
        """
        Set an OpenID response on my response's headers and body
        based on oidresponse, which should come from
        OpenIDRequest.answer() or handleRequest().
        """
        logging.debug(
            'respond: oidresponse.request.mode %s' % oidresponse.request.mode)
        # add extension fields if a qualifiying positve response
        if oidresponse.request.mode == 'checkid_setup':
            if oidresponse.fields.toArgs()['mode'] == 'id_res':
                oidresponse = self.add_sreg_fields(oidresponse, user)
        logging.info('respond: using response: %s' % oidresponse)
        self.render_response(oidresponse)
        
    def render_template(self, template_name, extra_values={}):
        """
        Render the given template to my response
        with various headers, values and given extra_values.
        """
        (scheme, netloc, path, dummy, dummy, dummy) = urlparse.urlparse(
            self.request.uri)
        request_url_without_path = scheme + '://' + netloc
        request_url_without_params = request_url_without_path + path

        self.response.headers.add_header(
            'X-XRDS-Location', request_url_without_path + '/xrds')
        values = {
            'request': self.request,
            'request_url_without_path': request_url_without_path,
            'request_url_without_params': request_url_without_params,
            'user': users.get_current_user(),
            'login_url': users.create_login_url(self.request.uri),
            'logout_url': users.create_logout_url('/')}
        values.update(extra_values)
        cwd = os.path.dirname(__file__)
        path = os.path.join(cwd, 'templates', template_name + '.html')
        self.response.out.write(template.render(path, values, debug=_DEBUG))
    
    def report_error(self, message):
        """
        Render an HTML error page to my response.
        """
        self.response.set_status(400)
        args = pprint.pformat(self.arg_map(self.request))
        self.render_template('error', {'args':args, 'message':message})
        logging.error(message)
    
    def store_login(self, oidrequest, kind):
        """
        Store a record of an OpenID login.
        """
        login = datastore.Entity('Login')
        login['relying_party'] = oidrequest.trust_root
        login['time'] = datetime.datetime.now()
        login['kind'] = kind
        login['user'] = users.get_current_user()
        datastore.Put(login)
    
    def check_user(self, user, request):
        """
        Return True if user matches request's claimed identity, else False,
        or None if there is no claimed identity
        """
        try:
            identity = self.arg_map(request)['openid.identity']
        except KeyError:
            return None
        if identity == 'http://specs.openid.net/auth/2.0/identifier_select':
            return True
        if user:
            if identity == self.get_identity_url(user, request):
                return True
        return False

    # XXX want to be able to config this somehow, start in conf
    def duo_username(self, user):
        """
        Return the username for user on the Duo server, or None.
        """
        if not user:
            return None
        return user.nickname()


class XRDS(Handler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/xrds+xml'
        self.response.out.write(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<xrds:XRDS xmlns:xrds="xri://$xrds" xmlns="xri://$xrd*($v*2.0)">'
            '<XRD>'
            '<Service priority="0">'
            '<Type>http://specs.openid.net/auth/2.0/server</Type>'
            '<Type>http://specs.openid.net/auth/2.0/signon</Type>'
            '<Type>http://openid.net/srv/ax/1.0</Type>'
            '<URI>%(op_endpoint)s</URI>'
            '</Service>'
            '</XRD>'
            '</xrds:XRDS>' % {'op_endpoint':oidserver.op_endpoint})


class UserXRDS(Handler):
    def get(self):
      self.response.headers['Content-Type'] = 'application/xrds+xml'
      self.response.out.write(
          '<?xml version="1.0" encoding="UTF-8"?>'
          '<xrds:XRDS xmlns:xrds="xri://$xrds" xmlns="xri://$xrd*($v*2.0)">'
          '<XRD>'
          '<Service priority="0">'
          '<Type>http://specs.openid.net/auth/2.0/signon</Type>'
          '<URI>%(op_endpoint)s</URI>'
          '</Service>'
          '</XRD>'
          '</xrds:XRDS>' % {'op_endpoint':oidserver.op_endpoint})


class FrontPage(Handler):
    """Show the default OpenID page, with the last 10 logins for this user."""
    def get(self):
        user = users.get_current_user()
        self.render_template('index', {'user':user, 'logins':self.logins(user)})


class Login(Handler):
    """
    Handles OpenID requests: associate, checkid_setup, checkid_immediate,
    check_authentication.
    """
    def post(self):
        try:
            oidrequest = oidserver.decodeRequest(self.arg_map(self.request))
            if oidrequest is None:
                self.report_error('no OpenID request')
                return
            self.verify_request(oidrequest, self.request)
        except OpenIDServer.ProtocolError, exc:
            self.render_response(exc)
            return
        logging.debug('Login: mode %s' % oidrequest.mode)

        if oidrequest.mode in ['associate', 'check_authentication']:
            logging.debug('Login: responding to %s' % oidrequest.mode)
            self.respond(oidserver.handleRequest(oidrequest))
            return
        elif oidrequest.mode in ['checkid_immediate', 'checkid_setup']:
            user = users.get_current_user()
            logging.debug('Login: user %s' % user)
            if user is None:
                logging.debug('Login: no user')
                if oidrequest.mode == 'checkid_immediate':
                    self.respond(oidrequest.answer(False))
                    return
                else:
                    # This will run into problems if the URL is too long,
                    # we're trying to stuff a POST into a GET.  A popup is
                    # probably the only safe way.
                    self.redirect(users.create_login_url(
                        '%s?%s' % (self.request.uri, urllib.urlencode(
                            self.arg_map(self.request)))))
                    return
            check_id = self.check_user(user, self.request)
            if check_id is None:
                logging.debug('Login: no identity')
                self.respond(oidrequest.answer(False))
                return
            elif not check_id:
                logging.debug('Login: wrong identity for user %s' % user)
                if oidrequest.mode == 'checkid_immediate':
                    self.respond(oidrequest.answer(False))
                    return
                else:
                    # Would be nicer to allow the user to login as the correct
                    # user and keep the auth flow
                    self.render_template(
                        'index', {'user':user, 'logins':self.logins(user)})
                    return
            identity_url = self.get_identity_url(user, self.request)
            if self.has_cookie(
                self.request, oidrequest.trust_root, identity_url):
                logging.debug('Login: has cookie, accepting')
                self.store_login(oidrequest, 'remembered')
                # provider SHOULD verify return_to
                #oidrequest.returnToVerified()
                self.respond(
                    oidrequest.answer(True, identity=identity_url), user)
                return
            else:
                if oidrequest.mode == 'checkid_immediate':
                    logging.debug('Login: declining')
                    self.respond(oidrequest.answer(False))
                    return
                else:
                    logging.debug('Login: prompting')
                    # Collect arguments for the template/JS to pass to
                    # our prompt.  Note that these could be modified by the
                    # user.
                    post_args = oidrequest.message.toPostArgs()
                    # these may have been identifier_select
                    post_args['openid.claimed_id'] = identity_url
                    post_args['openid.identity'] = identity_url
                    post_args['trust_root'] = oidrequest.trust_root
                    self.render_template(
                        'secondary_auth',
                        {'postargs':post_args,
                         'post_action':'/prompt',
                         'sig_request':duo_web.sign_request(
                             ikey, skey, akey, self.duo_username(user)),
                         'host':host})

    get = post


class Prompt(Handler):
    """
    Handle a POST response from the Duo authentication page.
    Prompt user to accept or deny authentication.
    """
    def post(self):
        duo_user = duo_web.verify_response(
            ikey, skey, akey, self.request.get('sig_response', ''))
        if duo_user is None:
            self.report_error('Improper Duo authentication for user.')
            return
        arg_map = self.arg_map(self.request)
        # post_args from odrequst.message all start with openid.
        post_args = dict([
            (key, val) for (key, val) in arg_map.items()
            if key.startswith('openid.')])
        self.render_template(
            'prompt',
            {'trust_root':arg_map['trust_root'],
             'user':users.get_current_user(),
             'action':'/login',
             'postargs':post_args})


class FinishLogin(Handler):
    """Handle a POST response to the OpenID login prompt form."""

    def post(self):
        logging.debug('FinishLogin')
        args = self.arg_map(self.request)
        try:
            from openid.message import Message
            message = Message.fromPostArgs(args)
            oidrequest = OpenIDServer.CheckIDRequest.fromMessage(
                message, oidserver.op_endpoint)
            self.verify_request(oidrequest, self.request)            
        except OpenIDServer.ProtocolError, exc:
            self.render_response(exc)
            return
 
        user = users.get_current_user()
        if not self.check_user(user, self.request):
            # Show human-readable response to a form post
            self.report_error('Attempted to authenticate to wrong identity')
            return
        logging.debug('FinishLogin: user %s' % user)

        if args.has_key('yes'):
            identity_url = self.get_identity_url(user, self.request)
            logging.debug('FinishLogin: confirming %s' % oidrequest.trust_root)

            if args.get('remember') == 'yes':
                logging.debug('FinishLogin: setting cookie')
                self.set_cookie(
                    self.response, oidrequest.trust_root, identity_url)

            self.store_login(oidrequest, 'confirmed')
            # provider SHOULD verify return_to
            #oidrequest.returnToVerified()
            answer = oidrequest.answer(True, identity=identity_url)
            logging.info('FinishLogin: answer: %s', answer)
            self.respond(answer, user)
        elif args.has_key('no'):
            logging.debug('FinishLogin: denying %s' % oidrequest.trust_root)
            self.store_login(oidrequest, 'declined')
            return self.respond(oidrequest.answer(False), user)
        else:
            # Show human-readable response to a form post; we could present
            # the form again.
            self.report_error("Missing authentication confirmation")


def initialize_globals(ikey, skey, akey, host, **kwargs):
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)-8s: %(message)s - %(pathname)s:%(lineno)d")
    logging.debug('start')
    initialize_open_id()
    initialize_app()
    initialize_duo(ikey, skey, akey, host)

def initialize_duo(ikey_, skey_, akey_, host_):
    global ikey, skey, akey, host
    if ikey is None or skey is None or akey is None or host is None:
        ikey = ikey_
        skey = skey_
        akey = akey_        
        host = host_

def initialize_open_id():
    """
    Initialize and set the global OpenID protocol server.
    """
    global oidserver
    if oidserver is None:
        # We have to use os.environ, the server uses it.
        name = os.environ.get('SERVER_NAME', None)
        port = os.environ.get('SERVER_PORT', '80')
        op_endpoint = "http://%s%s/server" % (
            name, ":%s" % port if port != "80" else "") if name else None
        logging.info('op_endpoint: %s', op_endpoint)
        oidserver = OpenIDServer.Server(
            store.DatastoreStore(), op_endpoint=op_endpoint)
        
def initialize_app():
    """
    Initialize and set the global WSGI application. 
    """
    global application
    if application is None:
        application = webapp.WSGIApplication(
            [('/', FrontPage),
             ('/server', Login),
             ('/login', FinishLogin),
             ('/prompt', Prompt),
             ('/xrds', XRDS),
             ('/[^/]*', UserXRDS)],
            debug=_DEBUG)
        
def main():
    duo_config = ConfigParser.ConfigParser()
    duo_config.read(duo_conf)
    
    initialize_globals(**dict(duo_config.items('duo')))
    run_wsgi_app(application)
    
if __name__ == '__main__':
    main()
