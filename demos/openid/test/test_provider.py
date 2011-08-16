import unittest
import os
import webtest
import urllib, urlparse
import hashlib
import mox

import appenginetest
import provider


class DuoWebMock(object):
    """
    Object to allow mox to mock the duo_web module.
    """
    def sign_request(self, ikey, skey, akey, username): pass
    def verify_response(self, ikey, skey, akey, sig_response): pass


class TestBase(unittest.TestCase, object):

    def setUp(self):
        # sigh, we need to use os.environ for the OpenID lib and some GAE stuff
        os.environ['SERVER_NAME'] = 'SERVER_NAME'
        os.environ['SERVER_PORT'] = '80'
        os.environ['APPLICATION_ID'] = 'APPLICATION_ID'
        for key in ['USER_EMAIL', 'USER_IS_ADMIN']:
            try:
                del os.environ[key]
            except KeyError:
                pass
        # Set up globals as done in initialize_globals
        #provider.initialize_globals()
        provider.initialize_open_id()
        provider.initialize_app()
        provider.initialize_duo(
            'test_ikey', 'test_skey', 'test_akey', 'test_host')
        self.app = webtest.TestApp(provider.application)

    def checkid_setup_request_environ(self):
        """
        Return a map suitable for the request environ of
        an OpenID checkid_setup request POST.
        """
        return {
            u'openid.return_to': u'http://relying.example.org/return',
            u'openid.realm': u'http://relying.example.org',
            u'openid.ns': u'http://specs.openid.net/auth/2.0',
            u'openid.claimed_id': u'http://localhost/foo@example.org',
            u'openid.mode': u'checkid_setup',
            u'openid.assoc_handle': u'{HMAC-SHA1}{4d06b59e}{rfT1Xw==}',
            u'openid.identity': u'http://localhost/foo@example.org'}

    def checkid_setup_select_request_environ(self):
        """
        Return a map suitable for the request environ of
        an OpenID checkid_setup request POST with an identitifer select
        claimed ID and identity.
        """
        env = self.checkid_setup_request_environ()
        env['openid.claimed_id'] = (
            u'http://specs.openid.net/auth/2.0/identifier_select')
        env['openid.identity'] = (
            u'http://specs.openid.net/auth/2.0/identifier_select')
        return env

    def checkid_immediate_request_environ(self):
        """
        Return a map suitable for the request environ of
        an OpenID checkid_immediate request POST.
        """
        env = self.checkid_setup_request_environ()
        env['openid.mode'] = 'checkid_immediate'
        return env

    def checkid_immediate_select_request_environ(self):
        """
        Return a map suitable for the request environ of
        an OpenID checkid_immediate request POST with an identitifer select
        claimed ID and identity.
        """
        env = self.checkid_setup_select_request_environ()
        env['openid.mode'] = 'checkid_immediate'
        return env

    def associate_request_environ(self):
        """
        Return a map suitable for the request environ of
        an OpenID associate request POST.
        """
        return {
            u'openid.session_type':'DH-SHA1',
            u'openid.dh_consumer_public':(
                'Upc2fv2sFP2E2W0ImiSyEOOU4CT16N7YdQ4ni4N+Nb8VxTNw7JwtopDnn'
                'lrkelRAUpkYfeMCaheow0fKyjrpp2Uf0N8UvcHPkgL0LHXz5SQFwgI0oD'
                '5b9FrQ3mWJPkuo6gsa+dn6iHTw1USY6XCv++iPHKbemqk4ShlVMkiKeCc='),
            u'openid.assoc_type':'HMAC-SHA1',
            u'openid.ns': u'http://specs.openid.net/auth/2.0',
            u'openid.mode': u'associate'}

    def check_authentication_request_environ(self):
        """
        Return a map suitable for the request environ of
        an OpenID check_authentication request POST.
        """
        return {
            u'openid.op_endpoint':'http://localhost:8080/server',
            u'openid.sig':'Nz9+QUOWUuDLqgKvxFOAO2GXjWg=',
            u'openid.return_to':u'http://relying.example.org/return',
            u'openid.ns':'http://specs.openid.net/auth/2.0',
            u'janrain_nonce':'2010-12-22T22:48:15Z1CLPJ5',
            u'openid.response_nonce':'2010-12-22T22:48:16ZQJwghT',
            u'openid.claimed_id': u'http://localhost/foo@example.org',
            u'openid.mode':'check_authentication',
            u'openid.signed':('assoc_handle,claimed_id,identity,mode,ns,'
                              'op_endpoint,response_nonce,return_to,signed'),
            u'openid.assoc_handle':'{HMAC-SHA1}{4d128030}{YDGdUg==}',
            u'openid.identity': u'http://localhost/foo@example.org'}

    def cookie_item(self, trust_root, identity_url):
        """
        Return an item suitable for a remember cookie
        for trust_root and identity_url in a request header.
        """
        # copy of Handler.cookie_key()
        cookie_key = 'openid_remembered_%s' % hashlib.md5(
            '%s %s' % (trust_root, identity_url)).hexdigest()
        return (cookie_key, 'yes')

    def check_redirect_login(
        self, response, identity='http://localhost/foo@example.org'):
        """
        Assert that response redirects to the login page with the OpenID
        request preserved.
        """
        identity = urllib.quote(urllib.quote(identity, safe=''))
        self.assertEqual(response.status_int, 302)
        self.assertEqual(
            response.headers['Location'],
            'https://www.google.com/accounts/Login?'
            'continue=http%3A//localhost/server%3Fopenid.ns%3D'
            'http%253A%252F%252Fspecs.openid.net%252Fauth%252F2.0'
            '%26openid.realm%3Dhttp%253A%252F%252Frelying.example.org'
            '%26openid.return_to%3Dhttp%253A%252F%252Frelying.example.org'
            '%252Freturn'
            '%26openid.claimed_id%3D' + identity +
            '%26openid.mode%3Dcheckid_setup'
            '%26openid.assoc_handle%3D%257BHMAC-SHA1%257D%257B4d06b59e%257D'
            '%257BrfT1Xw%253D%253D%257D'
            '%26openid.identity%3D' + identity)

    def check_redirect_positive(self, response):
        """
        Assert that response redirects to the RP return_to URL
        with a positive response.
        """
        self.assertEqual(response.status_int, 302)
        location = urlparse.urlparse(response.headers['Location'])
        self.assertEqual(location.netloc, 'relying.example.org')
        self.assertEqual(location.path, '/return')        
        query = urlparse.parse_qs(location.query)
        self.assertEqual(
            query['openid.op_endpoint'], ['http://SERVER_NAME/server'])
        self.assertEqual(
            query['openid.return_to'], ['http://relying.example.org/return'])
        self.assertEqual(
            query['openid.ns'], ['http://specs.openid.net/auth/2.0'])
        self.assertEqual(
            query['openid.claimed_id'], ['http://localhost/foo@example.org'])
        self.assertEqual(query['openid.mode'], [u'id_res'])
        self.assertEqual(
            query['openid.signed'],
            [u'assoc_handle,claimed_id,identity,invalidate_handle,mode,'
             'ns,op_endpoint,response_nonce,return_to,signed'])
        self.assertEqual(
            query['openid.identity'], ['http://localhost/foo@example.org'])

    def check_redirect_negative(self, response):
        """
        Assert that response redirects to the RP return_to URL
        with a negative response.
        """
        self.assertEqual(response.status_int, 302)
        location = urlparse.urlparse(response.headers['Location'])
        self.assertEqual(location.netloc, 'relying.example.org')
        self.assertEqual(location.path, '/return')        
        query = urlparse.parse_qs(location.query)
        self.assertEqual(query['openid.mode'], ['cancel'])
        self.assertEqual(
            query['openid.ns'], ['http://specs.openid.net/auth/2.0'])

    def check_redirect_immediate_negative(self, response):
        """
        Assert that response redirects to the RP return_to URL with a
        setup_needed response.
        """
        self.assertEqual(response.status_int, 302)
        location = urlparse.urlparse(response.headers['Location'])
        self.assertEqual(location.netloc, 'relying.example.org')
        self.assertEqual(location.path, '/return')        
        query = urlparse.parse_qs(location.query)
        self.assertEqual(query['openid.mode'], ['setup_needed'])
        self.assertEqual(
            query['openid.ns'], ['http://specs.openid.net/auth/2.0'])

    def check_redirect_error(self, response):
        """
        Assert that response redirects to the RP return_to URL
        with an error response.
        """
        self.assertEqual(response.status_int, 302)
        location = urlparse.urlparse(response.headers['Location'])
        self.assertEqual(location.netloc, 'relying.example.org')
        self.assertEqual(location.path, '/return')        
        query = urlparse.parse_qs(location.query)
        self.assertEqual(query['openid.mode'], ['error'])
        self.assertTrue(query.has_key('openid.error'))
        self.assertEqual(
            query['openid.ns'], ['http://specs.openid.net/auth/2.0'])

    def check_render_front_page(self, response):
        """
        Assert that response renders the front page.
        """
        self.assertEqual(response.status_int, 200)
        self.assertTrue('<span class="nickname">' not in response.body)
        self.assertTrue('<div class="openid-error">' not in response.body)

# XXX this isn't being tested currently
#     def check_render_auth_page(self, response):
#         """
#         Assert that response renders an authorization prompt page.
#         """
#         self.assertEqual(response.status_int, 200)
#         self.assertTrue(
#             '<input type="hidden" '
#             'name="openid.return_to" '
#             'value="http://relying.example.org/return" />'
#             in response.body)
#         self.assertTrue(
#             '<input type="hidden" name="openid.claimed_id" '
#             'value="http://localhost/foo@example.org" />' in response.body)

    def check_render_duo_auth_page(self, response):
        """
        Assert that response renders a Duo authorization page.
        """
        self.assertEqual(response.status_int, 200)
        body = response.body.replace('\n', ' ')
        self.assertTrue(
            "Duo.init({'host':'test_host', 'post_action':'/prompt', "
            "'sig_request':'test_sig_request'});"
            in body)
        
    def check_render_user_page(self, response):
        """
        Assert that response renders the user's page.
        """
        self.assertEqual(response.status_int, 200)
        self.assertTrue(
            '<span class="nickname">foo@example.org</span>' in response.body)
        # this isn't an OpenID error response
        self.assertTrue('<div class="openid-error">' not in response.body)
        # this isn't an auth prompt
        self.assertTrue('openid.claimed_id' not in response.body)

    def check_associate_response(self, response):
        """
        Assert that response answers an associate request.
        """
        self.assertEqual(response.status_int, 200)
        self.assertTrue('assoc_handle:{HMAC-SHA1}' in response.body)
        self.assertTrue('assoc_type:HMAC-SHA1' in response.body)
        self.assertTrue('ns:http://specs.openid.net/auth/2.0' in response.body)
        self.assertTrue('session_type:DH-SHA1' in response.body)


class TestUserXRDS(TestBase):
        
    def test_get(self):
        response = self.app.get('/foo')
        self.assertEqual(response.status_int, 200)        
        self.assertEqual(
            response.headers['Content-Type'], 'application/xrds+xml')
        self.assertEqual(
            response.body,
            ('<?xml version="1.0" encoding="UTF-8"?>'
             '<xrds:XRDS xmlns:xrds="xri://$xrds" xmlns="xri://$xrd*($v*2.0)">'
             '<XRD><Service priority="0">'
             '<Type>http://specs.openid.net/auth/2.0/signon</Type>'
             '<URI>http://SERVER_NAME/server</URI>'
             '</Service></XRD></xrds:XRDS>'))

    def test_post(self):
        """
        A POST should error 405.
        """
        try:
            response = self.app.post('/foo')
        except webtest.AppError, exc:
            self.assertEqual(exc.args[0].find('Bad response: 405'), 0)
        else:
            self.fail()


class TestLoginNoUser(
    appenginetest.NoUsersTest, appenginetest.DatastoreTest, TestBase):
    """
    Test the Login class with no authorized user.
    """

    def setUp(self):
        TestBase.setUp(self)
        appenginetest.DatastoreTest.setUp(self)        
        appenginetest.NoUsersTest.setUp(self)

    def test_post_checkid_setup_no_cookie(self):
        """
        A POST with no user logged in, an OpenID checkid_setup request,
        and no cookie should redirect to the login page.
        """
        response = self.app.post(
            '/server', self.checkid_setup_request_environ())
        self.check_redirect_login(response)

    def test_post_checkid_setup_select_no_cookie(self):
        """
        A POST with no user logged in, an OpenID checkid_setup request with
        an identifier_select identity,
        and no cookie should redirect to the login page.
        """
        response = self.app.post(
            '/server', self.checkid_setup_select_request_environ())
        self.check_redirect_login(
            response, 'http://specs.openid.net/auth/2.0/identifier_select')

    def test_post_checkid_setup_cookie(self):
        """
        A POST no user logged in, with an OpenID checkid_setup request,
        and a cookie matching the request should redirect to the login page.
        """
        self.app.cookies = dict(
            [self.cookie_item('http://relying.example.org',
                              'http://localhost/foo@example.org')])
        response = self.app.post(
            '/server', self.checkid_setup_request_environ())
        self.check_redirect_login(response)        

    def test_post_checkid_immediate_no_cookie(self):
        """
        A POST with no user logged in, an OpenID checkid_immediate request,
        and no cookie should return an indirect response with
        a negative assertion.
        """
        response = self.app.post(
            '/server', self.checkid_immediate_request_environ())
        self.check_redirect_immediate_negative(response)

    def test_post_checkid_immediate_select_no_cookie(self):
        """
        A POST with no user logged in, an OpenID checkid_immediate request
        with an identitifer_select identity,
        and no cookie should return an indirect response with
        a negative assertion.
        """
        response = self.app.post(
            '/server', self.checkid_immediate_select_request_environ())
        self.check_redirect_immediate_negative(response)

    def test_post_checkid_immediate_cookie(self):
        """
        A POST with no user logged in, an OpenID checkid_immediate request,
        and a cookie matching the request should return an indirect response
        with a negative assertion.
        """
        self.app.cookies = dict(
            [self.cookie_item('http://relying.example.org',
                              'http://localhost/foo@example.org')])
        response = self.app.post(
            '/server', self.checkid_immediate_request_environ())
        self.check_redirect_immediate_negative(response)        

    def test_post_checkid_immediate_select_cookie(self):
        """
        A POST with no user logged in, an OpenID checkid_immediate request
        with an identifier_select identity,
        and a cookie matching the request should return an indirect response
        with a negative assertion.
        """
        response = self.app.post(
            '/server', self.checkid_immediate_select_request_environ())
        self.check_redirect_immediate_negative(response)

    def test_post_associate(self):
        """
        A POST with no user logged in and an OpenID associate request
        should return an associate response.
        """
        response = self.app.post('/server', self.associate_request_environ())
        self.check_associate_response(response)

    # XXX to test a valid one, must make more requests, give results back
    def test_post_check_authentication_invalid(self):
        """
        A POST with no user logged in and an OpenID check_authentication request
        which fails should return an associate response.
        """
        response = self.app.post(
            '/server', self.check_authentication_request_environ())
        self.assertEqual(
            response.body,
            'is_valid:false\nns:http://specs.openid.net/auth/2.0\n')

    def test_post_bad_request_no_cookie(self):
        """
        A POST no user logged in, with an invalid OpenID request,
        and no cookie should return an indirect error response.
        """
        o_req = self.checkid_setup_request_environ()
        o_req['openid.mode'] = 'foobar'
        response = self.app.post('/server', o_req)
        self.check_redirect_error(response)        

    def test_post_bad_request_cookie(self):
        """
        A POST no user logged in, with an invalid OpenID request,
        and a cookie matching the request should return an indirect error
        response.
        """
        self.app.cookies = dict(
            [self.cookie_item('http://relying.example.org',
                              'http://localhost/foo@example.org')])
        o_req = self.checkid_setup_request_environ()
        o_req['openid.mode'] = 'foobar'
        response = self.app.post('/server', o_req)
        self.check_redirect_error(response)        

    def test_post_no_request_no_cookie(self):
        """
        A POST with no user logged in, no OpenID request, and no cookie
        should 400.
        """
        try:
            response = self.app.post('/server')
        except webtest.AppError, exc:
            self.assertEqual(exc.args[0].find('Bad response: 400'), 0)
        else:
            self.fail()

    def test_post_no_request_cookie(self):
        """
        A POST with no user logged in, no OpenID request and a cookie
        should 400.
        """
        self.app.cookies = dict(
            [self.cookie_item('http://relying.example.org',
                              'http://localhost/foo@example.org')])
        try:
            response = self.app.post('/server')
        except webtest.AppError, exc:
            self.assertEqual(exc.args[0].find('Bad response: 400'), 0)
        else:
            self.fail()


class TestLoginUser(
    appenginetest.UsersTest, appenginetest.DatastoreTest, TestBase):
    """
    Test the Login class with an authorized user.
    """

    def setUp(self):
        TestBase.setUp(self)
        provider.duo_web = mox.MockObject(DuoWebMock)
        appenginetest.DatastoreTest.setUp(self)
        appenginetest.UsersTest.setUp(
            self, user_email='foo@example.org', user_is_admin='')

    def tearDown(self):
        TestBase.tearDown(self)
        mox.Verify(provider.duo_web)

    def test_post_checkid_setup_no_cookie(self):
        """
        A POST with a user logged in, an OpenID checkid_setup request matching
        the user, and no cookie
        should present the Duo authorization page.
        """
        provider.duo_web.sign_request(
            'test_ikey', 'test_skey', 'test_akey', mox.IgnoreArg()).AndReturn(
            'test_sig_request')
        mox.Replay(provider.duo_web)
        
        response = self.app.post(
            '/server', self.checkid_setup_request_environ())
        self.check_render_duo_auth_page(response)
        
    def test_post_checkid_setup_wrong_user_no_cookie(self):
        """
        A POST with a user logged in, an OpenID checkid_setup request with
        the wrong user, and no cookie should render the user's page.
        """
        o_req = self.checkid_setup_request_environ()
        o_req['openid.identity'] = 'http://localhost/bar@example.org'
        response = self.app.post('/server', o_req)
        self.check_render_user_page(response)        
        # XXX this doesn't seem to preserve the flow if the user is directed
        # here during an OpenID auth without being logged in - we end up at
        # /sever w/o being redirected to RP

    # Not sure this is correct.  'OP SHOULD choose an Identifier that belongs
    # to the end user'.
    def test_post_checkid_setup_select_no_cookie(self):
        """
        A POST with a user logged in, an OpenID checkid_setup request
        with an identitifier_select identity, and no cookie
        should present the Duo authorization page.
        """
        provider.duo_web.sign_request(
            'test_ikey', 'test_skey', 'test_akey', mox.IgnoreArg()).AndReturn(
            'test_sig_request')
        mox.Replay(provider.duo_web)
        
        response = self.app.post(
            '/server', self.checkid_setup_select_request_environ())
        self.check_render_duo_auth_page(response)        
        
    def test_post_checkid_setup_cookie(self):
        """
        A POST with a user logged in, an OpenID checkid_setup request matching
        the user, and a cookie matching the user
        should redirect to the given RP URL with various OpenID query fields.
        """
        self.app.cookies = dict(
            [self.cookie_item('http://relying.example.org',
                              'http://localhost/foo@example.org')])
        response = self.app.post(
            '/server', self.checkid_setup_request_environ())
        self.check_redirect_positive(response)

    # Not sure this is correct.  'OP SHOULD choose an Identifier that belongs
    # to the end user'.
    def test_post_checkid_setup_select_cookie(self):
        """
        A POST with a user logged in, an OpenID checkid_setup
        with an identitifer_select identity,
        and a cookie matching the user
        should redirect to the given RP URL with various OpenID query fields.
        """
        self.app.cookies = dict(
            [self.cookie_item('http://relying.example.org',
                              'http://localhost/foo@example.org')])
        response = self.app.post(
            '/server', self.checkid_setup_select_request_environ())
        self.check_redirect_positive(response)        

    def test_post_checkid_setup_wrong_user_cookie(self):
        """
        A POST with a user logged in, an OpenID checkid_setup request with
        the wrong user, and a cookie matching the user
        should render the user's page.
        """
        self.app.cookies = dict(
            [self.cookie_item('http://relying.example.org',
                              'http://localhost/foo@example.org')])
        o_req = self.checkid_setup_request_environ()
        o_req['openid.identity'] = 'http://localhost/bar@example.org'
        response = self.app.post('/server', o_req)
        self.check_render_user_page(response)        
        # XXX this doesn't seem to preserve the flow if the user is directed
        # here during an OpenID auth without being logged in - we end up at
        # /sever w/o being redirected to RP

    def test_post_checkid_setup_wrong_cookie(self):
        """
        A POST with a user logged in, an OpenID checkid_setup request matching
        the user, and a cookie that doesn't match the user
        should render the Duo authorization page.
        """
        provider.duo_web.sign_request(
            'test_ikey', 'test_skey', 'test_akey', mox.IgnoreArg()).AndReturn(
            'test_sig_request')
        mox.Replay(provider.duo_web)
        
        self.app.cookies = dict(
            [self.cookie_item('http://relying.example.org',
                              'http://localhost/bar@example.org')])
        response = self.app.post(
            '/server', self.checkid_setup_request_environ())
        self.check_render_duo_auth_page(response)        

    def test_post_checkid_setup_select_wrong_cookie(self):
        """
        A POST with a user logged in, an OpenID checkid_setup
        with an identitifer_select identity,
        and a cookie that doesn't match the user
        should render the Duo authorization page.
        """
        provider.duo_web.sign_request(
            'test_ikey', 'test_skey', 'test_akey', mox.IgnoreArg()).AndReturn(
            'test_sig_request')
        mox.Replay(provider.duo_web)
        
        self.app.cookies = dict(
            [self.cookie_item('http://relying.example.org',
                              'http://localhost/bar@example.org')])
        response = self.app.post(
            '/server', self.checkid_setup_select_request_environ())
        self.check_render_duo_auth_page(response)

    def test_post_checkid_setup_wrong_user_wrong_cookie(self):
        """
        A POST with a user logged in, an OpenID checkid_setup request with
        the the wrong user, and a cookie that doesn't match the user
        should render the user's page.
        """
        self.app.cookies = dict(
            [self.cookie_item('http://relying.example.org',
                              'http://localhost/bar@example.org')])
        o_req = self.checkid_setup_request_environ()
        o_req['openid.identity'] = 'http://localhost/bar@example.org'
        response = self.app.post('/server', o_req)
        self.check_render_user_page(response)        
        # XXX this doesn't seem to preserve the flow if the user is directed
        # here during an OpenID auth without being logged in - we end up at
        # /sever w/o being redirected to RP

    def test_post_checkid_immediate_no_cookie(self):
        """
        A POST with a user logged in, an OpenID checkid_immediate request
        matching the user, and no cookie should return a redirect with a
        negative assertion.
        """
        response = self.app.post(
            '/server', self.checkid_immediate_request_environ())
        self.check_redirect_immediate_negative(response)

    def test_post_checkid_immediate_select_no_cookie(self):
        """
        A POST with a user logged in, an OpenID checkid_immediate request
        with an identitifer_select identity,
        and no cookie should return a redirect with a
        negative assertion.
        """
        response = self.app.post(
            '/server', self.checkid_immediate_select_request_environ())
        self.check_redirect_immediate_negative(response)

    def test_post_checkid_immediate_wrong_user_no_cookie(self):
        """
        A POST with a user logged in, an OpenID checkid_immediate request
        with the wrong user, and no cookie should return a redirect with a
        negative assertion.
        """
        o_req = self.checkid_immediate_request_environ()    
        o_req['openid.identity'] = 'http://localhost/bar@example.org'    
        response = self.app.post('/server', o_req)
        self.check_redirect_immediate_negative(response)

    def test_post_checkid_immediate_cookie(self):
        """
        A POST with a user logged in, an OpenID checkid_immediate request
        matching the user, and a cookie matching the user should authenticate
        the user.
        """
        self.app.cookies = dict(
            [self.cookie_item('http://relying.example.org',
                              'http://localhost/foo@example.org')])
        response = self.app.post(
            '/server', self.checkid_immediate_request_environ())
        self.check_redirect_positive(response)        

    # Not sure this is correct.  'OP SHOULD choose an Identifier that belongs
    # to the end user'.
    def test_post_checkid_immediate_select_cookie(self):
        """
        A POST with a user logged in, an OpenID checkid_immediate request
        with an identifier_select identity,
        and a cookie matching the user should authenticate the user.
        """
        self.app.cookies = dict(
            [self.cookie_item('http://relying.example.org',
                              'http://localhost/foo@example.org')])
        response = self.app.post(
            '/server', self.checkid_immediate_request_environ())
        self.check_redirect_positive(response)

    def test_post_checkid_immediate_select_wrong_cookie(self):
        """
        A POST with a user logged in, an OpenID checkid_immediate request
        with an identifier_select identity,
        and a cookie that doesn't match the user should return a redirect with a
        negative assertion.
        """
        self.app.cookies = dict(
            [self.cookie_item('http://relying.example.org',
                              'http://localhost/bar@example.org')])
        response = self.app.post(
            '/server', self.checkid_immediate_request_environ())
        self.check_redirect_immediate_negative(response)

    def test_post_checkid_immediate_wrong_user_cookie(self):
        """
        A POST with a user logged in, an OpenID checkid_immediate request
        with the wrong user, and a cookie matching the user should return a
        redirect with a negative assertion.
        """
        self.app.cookies = dict(
            [self.cookie_item('http://relying.example.org',
                              'http://localhost/foo@example.org')])
        o_req = self.checkid_immediate_request_environ()    
        o_req['openid.identity'] = 'http://localhost/bar@example.org'    
        response = self.app.post('/server', o_req)
        self.check_redirect_immediate_negative(response)

    def test_post_checkid_immediate_wrong_user_wrong_cookie(self):
        """
        A POST with a user logged in, an OpenID checkid_immediate request
        with the wrong user, and a cookie that doesn't match the user should
        return a redirect with a negative assertion.        
        """
        self.app.cookies = dict(
            [self.cookie_item('http://relying.example.org',
                              'http://localhost/bar@example.org')])
        o_req = self.checkid_immediate_request_environ()    
        o_req['openid.identity'] = 'http://localhost/bar@example.org'    
        response = self.app.post('/server', o_req)
        self.check_redirect_immediate_negative(response)

    def test_post_associate(self):
        """
        A POST with a user logged in and an OpenID associate request
        should return an associate response.
        """
        response = self.app.post('/server', self.associate_request_environ())
        self.check_associate_response(response)

    # XXX to test a valid one, must make more requests, give results back
    def test_post_check_authentication_invalid(self):
        """
        A POST with a user logged in and an OpenID check_authentication request
        which fails should return an associate response.
        """
        response = self.app.post(
            '/server', self.check_authentication_request_environ())
        self.assertEqual(
            response.body,
            'is_valid:false\nns:http://specs.openid.net/auth/2.0\n')

    def test_post_bad_request_no_cookie(self):
        """
        A POST with a user logged in and an invalid OpenID request should
        return an indirect error response.
        """
        o_req = self.checkid_setup_request_environ()
        o_req['openid.mode'] = 'foobar'
        response = self.app.post('/server', o_req)
        self.check_redirect_error(response)        

    def test_post_bad_request_cookie(self):
        """
        A POST with a user logged in, an invalid OpenID request, and a cookie
        that matches the user should return an indirect error response.
        """
        o_req = self.checkid_setup_request_environ()
        o_req['openid.mode'] = 'foobar'
        self.app.cookies = dict(
            [self.cookie_item('http://relying.example.org',
                              'http://localhost/foo@example.org')])
        response = self.app.post('/server', o_req)
        self.check_redirect_error(response)        

    def test_post_bad_request_wrong_cookie(self):
        """
        A POST with a user logged in, an invalid OpenID request, and a cookie
        that doesn't match the user should return an indirect error response.
        """
        o_req = self.checkid_setup_request_environ()
        o_req['openid.mode'] = 'foobar'
        self.app.cookies = dict(
            [self.cookie_item('http://relying.example.org',
                              'http://localhost/bar@example.org')])
        response = self.app.post('/server', o_req)
        self.check_redirect_error(response)        

    def test_post_no_request_no_cookie(self):
        """
        A POST with a user logged in and no OpenID request should 400.
        """
        try:
            response = self.app.post('/server')
        except webtest.AppError, exc:
            self.assertEqual(exc.args[0].find('Bad response: 400'), 0)
        else:
            self.fail()

    def test_post_no_request_cookie(self):
        """
        A POST with a user logged in, no OpenID request, and a cookie that
        matches the user should 400.
        """
        self.app.cookies = dict(
            [self.cookie_item('http://relying.example.org',
                              'http://localhost/foo@example.org')])
        try:
            response = self.app.post('/server')
        except webtest.AppError, exc:
            self.assertEqual(exc.args[0].find('Bad response: 400'), 0)
        else:
            self.fail()

    def test_post_no_request_wrong_cookie(self):
        """
        A POST with a user logged in, no OpenID request, and a cookie
        that doesn't match the user should 400.
        """
        self.app.cookies = dict(
            [self.cookie_item('http://relying.example.org',
                              'http://localhost/bar@example.org')])
        try:
            response = self.app.post('/server')
        except webtest.AppError, exc:
            self.assertEqual(exc.args[0].find('Bad response: 400'), 0)
        else:
            self.fail()


class TestFinishLoginNoUser(appenginetest.NoUsersTest, TestBase):
    """
    Test the FinishLogin class with no authorized user.
    """

    def setUp(self):
        TestBase.setUp(self)        
        appenginetest.NoUsersTest.setUp(self)

    def test_post_auth(self):
        """
        A POST with no user logged in and an authorized OpenID
        request should 400.
        """
        try:
            response = self.app.post(
                '/login', dict(self.checkid_setup_request_environ(), yes='yes'))
        except webtest.AppError, exc:
            self.assertEqual(exc.args[0].find("Bad response: 400"), 0)
        else:
            self.fail()

    def test_post_unauth(self):
        """
        A POST with no user logged in and an authorized OpenID
        request should 400.
        """
        try:
            response = self.app.post(
                '/login', dict(self.checkid_setup_request_environ(), yes='no'))
        except webtest.AppError, exc:
            self.assertEqual(exc.args[0].find("Bad response: 400"), 0)
        else:
            self.fail()

    def test_post_no_auth(self):
        """
        A POST with no user logged in and no authorization given should 400.
        """
        try:
            response = self.app.post(
                '/login', self.checkid_setup_request_environ())
        except webtest.AppError, exc:
            self.assertEqual(exc.args[0].find("Bad response: 400"), 0)
        else:
            self.fail()

    def test_post_bad_request(self):
        """
        A POST with no user logged in and an invalid OpenID request should
        return an indirect error response.
        """
        o_req = self.checkid_setup_request_environ()
        o_req['openid.realm'] = 'foobar'
        o_req['yes'] = 'Yes'
        response = self.app.post('/login', o_req)
        self.check_redirect_error(response)        

    def test_post_no_request(self):
        """
        A POST with no user logged in and no OpenID request should 400.
        """
        try:
            response = self.app.post('/login')
        except webtest.AppError, exc:
            self.assertEqual(exc.args[0].find("Bad response: 400"), 0)
        else:
            self.fail()
 

class TestFinishLoginUser(
    appenginetest.UsersTest, appenginetest.DatastoreTest, TestBase):
    """
    Test the FinishLogin class with an authorized user.
    """

    def setUp(self):
        TestBase.setUp(self)        
        appenginetest.DatastoreTest.setUp(self)
        appenginetest.UsersTest.setUp(
            self, user_email='foo@example.org', user_is_admin='')

    def test_post_auth(self):
        """
        A POST with a user logged in and an authorized OpenID request
        that matches the user
        should redirect to the given RP URL with various OpenID query fields.
        """
        response = self.app.post(
            '/login', dict(self.checkid_setup_request_environ(), yes='yes'))
        self.check_redirect_positive(response)

    def test_post_auth_wrong_user(self):
        """
        A POST with a user logged in and an authorized OpenID request
        that doesn't match the user
        should 400.
        """
        o_req = self.checkid_setup_request_environ()
        o_req['openid.identity'] = 'http://localhost/bar@example.org'
        try:
            response = self.app.post('/login', o_req)
        except webtest.AppError, exc:
            self.assertEqual(exc.args[0].find('Bad response: 400'), 0)
        else:
            self.fail()

    def test_post_unauth(self):
        """
        A POST with a user logged in and an unauthorized OpenID request
        that matches the user
        should redirect to the given RP URL with various OpenID query fields.
        """
        response = self.app.post(
            '/login', dict(self.checkid_setup_request_environ(), no='no'))
        self.check_redirect_negative(response)

    def test_post_unauth_wrong_user(self):
        """
        A POST with a user logged in and an unauthorized OpenID request
        that doesn't match the user should 400.
        """
        o_req = self.checkid_setup_request_environ()
        o_req['openid.identity'] = 'http://localhost/bar@example.org'
        o_req['no'] = 'no'
        try:
            response = self.app.post('/login', o_req)
        except webtest.AppError, exc:
            self.assertEqual(exc.args[0].find('Bad response: 400'), 0)
        else:
            self.fail()

    def test_post_no_auth(self):
        """
        A POST with a user logged in and an OpenID request without
        authorization that matches the user should 400.
        """
        try:
            response = self.app.post(
                '/login', self.checkid_setup_request_environ())
        except webtest.AppError, exc:
            self.assertEqual(exc.args[0].find("Bad response: 400"), 0)
        else:
            self.fail()

    def test_post_no_auth_wrong_user(self):
        """
        A POST with a user logged in and an OpenID request without
        authorization that matches the user should 400.
        """
        o_req = self.checkid_setup_request_environ()
        o_req['openid.identity'] = 'http://localhost/bar@example.org'
        try:
            response = self.app.post('/login', o_req)
        except webtest.AppError, exc:
            self.assertEqual(exc.args[0].find('Bad response: 400'), 0)
        else:
            self.fail()

    def test_post_bad_request(self):
        """
        A POST with a user logged in and an invalid OpenID request
        should return an indirect error response.
        """
        o_req = self.checkid_setup_request_environ()
        o_req['openid.realm'] = 'foobar'
        o_req['yes'] = 'Yes'
        response = self.app.post('/login', o_req)
        self.check_redirect_error(response)        

    def test_post_no_request(self):
        """
        A POST with a user logged in and no OpenID request
        should redirect to the user's page.
        """
        try:
            response = self.app.post('/login')
        except webtest.AppError, exc:
            self.assertEqual(exc.args[0].find("Bad response: 400"), 0)
        else:
            self.fail()
        
