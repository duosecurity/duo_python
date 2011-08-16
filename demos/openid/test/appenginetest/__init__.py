import os
import unittest
import logging

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.api import mail_stub
from google.appengine.api import user_service_stub
#from google.appengine.api.images import images_stub
#from google.appengine.api.images import images_not_implemented_stub as images_stub
from google.appengine.api.labs.taskqueue import taskqueue_stub
from google.appengine.api.memcache import memcache_stub
from google.appengine.api.xmpp import xmpp_service_stub

import test_capabilities


class AppEngineTest(unittest.TestCase):
  def setUp(self, disabled_capabilities=None, disabled_methods=None):
    """Setup routine for App Engine test cases.
    
    Args:
      disabled_capabilities: A set of (package, capability) tuples defining
        capabilities that are disabled.
      disabled_methods: A set of (package, method) tuples defining methods that
        are disabled. An entry of ('package', '*') in disabled_capabilities is
        treated the same as finding the method being tested in this set.
    """
    # Set up a new set of stubs for each test
    self.stub_map = apiproxy_stub_map.APIProxyStubMap()
    apiproxy_stub_map.apiproxy = self.stub_map
    
    if disabled_capabilities:
      self.disabled_capabilities = disabled_capabilities
    else:
      self.disabled_capabilities = set()
    if disabled_methods:
      self.disabled_methods = disabled_methods
    else:
      self.disabled_methods = set()
    capability_stub = test_capabilities.CapabilityServiceStub(
        self.disabled_capabilities, self.disabled_methods)
    self.stub_map.RegisterStub('capability_service', capability_stub)

  def _RegisterStub(self, service_name, stub):
    wrapped_stub = test_capabilities.CapabilityStubWrapper(stub,
        self.disabled_capabilities, self.disabled_methods)
    self.stub_map.RegisterStub(service_name, wrapped_stub)


class DatastoreTest(AppEngineTest):
  def setUp(self, datastore_file=None, history_file=None, require_indexes=False,
            **kwargs):
    super(DatastoreTest, self).setUp(**kwargs)
    stub = datastore_file_stub.DatastoreFileStub(
        os.environ['APPLICATION_ID'],
        datastore_file,
        history_file,
        require_indexes)
    self._RegisterStub('datastore_v3', stub)


class MemcacheTest(AppEngineTest):
  def setUp(self, **kwargs):
    super(MemcacheTest, self).setUp(**kwargs)
    stub = memcache_stub.MemcacheServiceStub()
    self._RegisterStub('memcache', stub)


class NoUsersTest(AppEngineTest):
  def setUp(self, user_email=None, user_is_admin=False, **kwargs):
    super(NoUsersTest, self).setUp(**kwargs)
    stub = user_service_stub.UserServiceStub()
    self._RegisterStub('user', stub)


class UsersTest(NoUsersTest):
  def setUp(self, user_email=None, user_is_admin=False, **kwargs):
    super(UsersTest, self).setUp(**kwargs)
    self.SetUser(user_email, user_is_admin)

  def SetUser(self, user_email, user_is_admin=False):
    os.environ['USER_EMAIL'] = user_email
    os.environ['USER_IS_ADMIN'] = user_is_admin

    
# TODO: Better test-oriented implementations of Mail, XMPP, URLFetch stubs


class MailTest(AppEngineTest):
  def setUp(self, **kwargs):
    super(MailTest, self).setUp(**kwargs)
    stub = mail_stub.MailServiceStub()
    self._RegisterStub('mail', stub)


class ImagesTest(AppEngineTest):
  def setUp(self, **kwargs):
    super(ImagesTest, self).setUp(**kwargs)
    stub = images_stub.ImagesServiceStub()
    self._RegisterStub('images', stub)


class XmppTest(AppEngineTest):
  def setUp(self, xmpp_log=logging.info, **kwargs):
    super(XmppTest, self).setUp(**kwargs)
    stub = xmpp_service_stub.XmppServiceStub(log=xmpp_log)
    self._RegisterStub('xmpp', stub)


class TaskQueueTest(AppEngineTest):
  def setUp(self, **kwargs):
    super(XmppTest, self).setUp(**kwargs)
    stub = taskqueue_stub.TaskQueueServiceStub()
    self._RegisterStub('taskqueue', self)


def main(app_id, auth_domain='gmail.com',
         server_software='Development/1.0 (AppEngineTest)'):
  os.environ['APPLICATION_ID'] = app_id
  os.environ['AUTH_DOMAIN'] = auth_domain
  os.environ['SERVER_SOFTWARE'] = server_software
  unittest.main()
