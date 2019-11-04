#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Simple tests for Duo Web SDK'''

import unittest
import duo_web
import sys

IKEY = "DIXXXXXXXXXXXXXXXXXX"
WRONG_IKEY = "DIXXXXXXXXXXXXXXXXXY"
SKEY = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
AKEY = "useacustomerprovidedapplicationsecretkey"

USER = "testuser"

INVALID_RESPONSE = "AUTH|INVALID|SIG"
EXPIRED_RESPONSE = "AUTH|dGVzdHVzZXJ8RElYWFhYWFhYWFhYWFhYWFhYWFh8MTMwMDE1Nzg3NA==|cb8f4d60ec7c261394cd5ee5a17e46ca7440d702"
FUTURE_RESPONSE = "AUTH|dGVzdHVzZXJ8RElYWFhYWFhYWFhYWFhYWFhYWFh8MTYxNTcyNzI0Mw==|d20ad0d1e62d84b00a3e74ec201a5917e77b6aef"
FUTURE_ENROLL_RESPONSE = "ENROLL|dGVzdHVzZXJ8RElYWFhYWFhYWFhYWFhYWFhYWFh8MTYxNTcyNzI0Mw==|74a0bcc807d40c828b448512f442dce46a85aa24"
WRONG_PARAMS_RESPONSE = "AUTH|dGVzdHVzZXJ8RElYWFhYWFhYWFhYWFhYWFhYWFh8MTYxNTcyNzI0M3xpbnZhbGlkZXh0cmFkYXRh|6cdbec0fbfa0d3f335c76b0786a4a18eac6cdca7"
WRONG_PARAMS_APP = "APP|dGVzdHVzZXJ8RElYWFhYWFhYWFhYWFhYWFhYWFh8MTYxNTcyNzI0M3xpbnZhbGlkZXh0cmFkYXRh|7c2065ea122d028b03ef0295a4b4c5521823b9b5"


class TestSDK(unittest.TestCase):

    def test_sign_request(self):
        request_sig = duo_web.sign_request(IKEY, SKEY, AKEY, USER)
        self.assertNotEqual(request_sig, None)

        request_sig = duo_web.sign_request(IKEY, SKEY, AKEY, '')
        self.assertEqual(request_sig, duo_web.ERR_USER)

        request_sig = duo_web.sign_request(IKEY, SKEY, AKEY, 'in|valid')
        self.assertEqual(request_sig, duo_web.ERR_USER)

        request_sig = duo_web.sign_request('invalid', SKEY, AKEY, USER)
        self.assertEqual(request_sig, duo_web.ERR_IKEY)

        request_sig = duo_web.sign_request(IKEY, 'invalid', AKEY, USER)
        self.assertEqual(request_sig, duo_web.ERR_SKEY)

        request_sig = duo_web.sign_request(IKEY, SKEY, 'invalid', USER)
        self.assertEqual(request_sig, duo_web.ERR_AKEY)

    def test_sign_request_bytestring_username(self):
        """
        Tests that duo_web will produce an encoding error for bytestring
        usernames in Python 3 (you cannot encode a bytes object in PY3)
        and will reject bytestring usernames in PY2 if they contain non-ASCII
        characters.
        """
        if sys.version_info[0] == 2:
            username = bytes("testüser")
        else:
            username = bytes("testüser", "utf-8")
        bytestring_request_sig = duo_web.sign_request(
            IKEY, SKEY, AKEY, username)
        self.assertEqual(duo_web.ERR_USER_ENCODING, bytestring_request_sig)

    def test_verify_response(self):
        request_sig = duo_web.sign_request(IKEY, SKEY, AKEY, USER)
        duo_sig, valid_app_sig = request_sig.split(':')

        request_sig = duo_web.sign_request(IKEY, SKEY, 'invalid' * 6, USER)
        duo_sig, invalid_app_sig = request_sig.split(':')

        request_sig = duo_web.sign_enroll_request(IKEY, SKEY, AKEY, USER)
        duo_sig, valid_enroll_sig = request_sig.split(':')

        request_sig = duo_web.sign_enroll_request(IKEY, SKEY, 'invalid' * 6, USER)
        duo_sig, invalid_enroll_sig = request_sig.split(':')

        invalid_user = duo_web.verify_response(IKEY, SKEY, AKEY, INVALID_RESPONSE + ':' + valid_app_sig)
        self.assertEqual(invalid_user, None)

        expired_user = duo_web.verify_response(IKEY, SKEY, AKEY, EXPIRED_RESPONSE + ':' + valid_app_sig)
        self.assertEqual(expired_user, None)

        future_user = duo_web.verify_response(IKEY, SKEY, AKEY, FUTURE_RESPONSE + ':' + invalid_app_sig)
        self.assertEqual(future_user, None)

        future_user = duo_web.verify_response(IKEY, SKEY, AKEY, FUTURE_RESPONSE + ':' + valid_app_sig)
        self.assertEqual(future_user, USER)

        future_user = duo_web.verify_response(IKEY, SKEY, AKEY, WRONG_PARAMS_RESPONSE + ':' + valid_app_sig)
        self.assertEqual(future_user, None)

        future_user = duo_web.verify_response(IKEY, SKEY, AKEY, FUTURE_RESPONSE + ':' + WRONG_PARAMS_APP)
        self.assertEqual(future_user, None)

        future_user = duo_web.verify_response(WRONG_IKEY, SKEY, AKEY, FUTURE_RESPONSE + ':' + valid_app_sig)
        self.assertEqual(future_user, None)

        enroll_user = duo_web.verify_enroll_response(IKEY, SKEY, AKEY, FUTURE_ENROLL_RESPONSE + ':' + valid_enroll_sig)
        self.assertEqual(enroll_user, USER)

        enroll_user = duo_web.verify_enroll_response(IKEY, SKEY, AKEY, FUTURE_ENROLL_RESPONSE + ':' + invalid_enroll_sig)
        self.assertEqual(enroll_user, None)


if __name__ == '__main__':
    unittest.main()
