from google.appengine.api import apiproxy_rpc
from google.appengine.api import apiproxy_stub
from google.appengine.api import capabilities
from google.appengine.runtime import apiproxy_errors

IsEnabledRequest = capabilities.IsEnabledRequest
IsEnabledResponse = capabilities.IsEnabledResponse
CapabilityConfig = capabilities.CapabilityConfig

class CapabilityServiceStub(apiproxy_stub.APIProxyStub):
  """Test-oriented capability service stub."""

  def __init__(self, disabled_capabilities, disabled_methods,
               service_name='capability_service'):
    """Constructor.

    Args:
      disabled_capabilities: A set of (package, capability) tuples defining
        capabilities that are disabled.
      disabled_methods: A set of (package, method) tuples defining methods that
        are disabled. An entry of ('package', '*') in disabled_capabilities
        is treated the same as finding the method being tested in this set.
      service_name: Service name expected for all calls.
    """
    super(CapabilityServiceStub, self).__init__(service_name)
    self.disabled_capabilities = disabled_capabilities
    self.disabled_methods = disabled_methods

  def _Dynamic_IsEnabled(self, request, response):
    """Implementation of CapabilityService::IsEnabled().

    Args:
      request: An IsEnabledRequest.
      response: An IsEnabledResponse.
    """
    package = request.package()
    if (package, '*') in self.disabled_capabilities:
      response.set_summary_status(IsEnabledRequest.DISABLED)
      config = response.add_config()
      config.set_package(package)
      config.set_capability('*')
      config.set_status(CapabilityConfig.DISABLED)
    else:
      any_disabled = False
      for method in request.call_list():
        config = response.add_config()
        config.set_package(package)
        config.set_capability(method)
        if (package, method) in self.disabled_methods:
          config.set_status(IsEnabledResponse.DISABLED)
          any_disabled = True
        else:
          config.set_status(IsEnabledResponse.ENABLED)
      for capability in request.capability_list():
        config = response.add_config()
        config.set_package(package)
        config.set_capability(capability)
        if (package, capability) in self.disabled_capabilities:
          any_disabled = True
          config.set_status(IsEnabledResponse.DISABLED)
        else:
          config.set_status(IsEnabledResponse.ENABLED)
    response.set_summary_status(IsEnabledResponse.DISABLED if any_disabled
                                else IsEnabledResponse.ENABLED)


class CapabilityStubWrapper(object):
  """A wrapper for stubs that raises CapabilityDisabledError when needed."""

  def __init__(self, wrapped_stub, disabled_capabilities, disabled_methods):
    self.wrapped_stub = wrapped_stub
    self.disabled_capabilities = disabled_capabilities
    self.disabled_methods = disabled_methods

  def CreateRPC(self):
    """Creates a (dummy) RPC object instance."""
    return apiproxy_rpc.RPC(stub=self)

  def MakeSyncCall(self, service, call, request, response):
    if ((service, '*') in self.disabled_capabilities
        or (service, call) in self.disabled_methods):
      raise apiproxy_errors.CapabilityDisabledError()
    self.wrapped_stub.MakeSyncCall(service, call, request, response)
