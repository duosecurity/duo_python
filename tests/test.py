#!/usr/bin/env python

'''Simple tests for Duo Web SDK'''

import unittest
import duo_web

IKEY = "DIXXXXXXXXXXXXXXXXXX"
SKEY = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
AKEY = "useacustomerprovidedapplicationsecretkey"

USER = "testuser"

INVALID_RESPONSE = "AUTH|INVALID|SIG"
EXPIRED_RESPONSE = "AUTH|dGVzdHVzZXJ8RElYWFhYWFhYWFhYWFhYWFhYWFh8MTMwMDE1Nzg3NA==|cb8f4d60ec7c261394cd5ee5a17e46ca7440d702"
FUTURE_RESPONSE = "AUTH|dGVzdHVzZXJ8RElYWFhYWFhYWFhYWFhYWFhYWFh8MTYxNTcyNzI0Mw==|d20ad0d1e62d84b00a3e74ec201a5917e77b6aef"

class TestSDK(unittest.TestCase):

    def test_sign_request(self):
        request_sig = duo_web.sign_request(IKEY, SKEY, AKEY, USER)
        self.assertNotEqual(request_sig, None)

        request_sig = duo_web.sign_request(IKEY, SKEY, AKEY, '')
        self.assertEqual(request_sig, duo_web.ERR_USER)

        request_sig = duo_web.sign_request('invalid', SKEY, AKEY, USER)
        self.assertEqual(request_sig, duo_web.ERR_IKEY)

        request_sig = duo_web.sign_request(IKEY, 'invalid', AKEY, USER)
        self.assertEqual(request_sig, duo_web.ERR_SKEY)

        request_sig = duo_web.sign_request(IKEY, SKEY, 'invalid', USER)
        self.assertEqual(request_sig, duo_web.ERR_AKEY)

    def test_verify_response(self):
        request_sig = duo_web.sign_request(IKEY, SKEY, AKEY, USER)
        duo_sig, valid_app_sig = request_sig.split(':')

        request_sig = duo_web.sign_request(IKEY, SKEY, 'invalid' * 6, USER)
        duo_sig, invalid_app_sig = request_sig.split(':')

        invalid_user = duo_web.verify_response(IKEY, SKEY, AKEY, INVALID_RESPONSE + ':' + valid_app_sig)
        self.assertEqual(invalid_user, None)

        expired_user = duo_web.verify_response(IKEY, SKEY, AKEY, EXPIRED_RESPONSE + ':' + valid_app_sig)
        self.assertEqual(expired_user, None)

        future_user = duo_web.verify_response(IKEY, SKEY, AKEY, FUTURE_RESPONSE + ':' + invalid_app_sig)
        self.assertEqual(future_user, None)

        future_user = duo_web.verify_response(IKEY, SKEY, AKEY, FUTURE_RESPONSE + ':' + valid_app_sig)
        self.assertEqual(future_user, USER)

if __name__ == '__main__':
    unittest.main()
