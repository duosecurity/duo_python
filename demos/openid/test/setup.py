"""
GAE test helpers.
Real tests will probably want to use a real fixture.
"""

import sys, os

def setup_path():
    """
    Get GAE libs into sys.path, adapted from dev_appserver.py.
    """
    # OSX
    #dir_path = os.path.abspath(os.path.join(
    #    '/',
    #    'Applications', 'GoogleAppEngineLauncher.app', 'Contents',
    #     'Resources',
    #     'GoogleAppEngine-default.bundle', 'Contents', 'Resources',
    #     'google_appengine'))
    # CentOS
    dir_path = '/usr/local/bin/google_appengine/'

    extra_paths = [
      dir_path,
      os.path.join(dir_path, 'lib', 'antlr3'),
      os.path.join(dir_path, 'lib', 'django'),
      os.path.join(dir_path, 'lib', 'fancy_urllib'),
      os.path.join(dir_path, 'lib', 'ipaddr'),
      os.path.join(dir_path, 'lib', 'webob'),
      os.path.join(dir_path, 'lib', 'yaml', 'lib'),
    ]
        
    sys.path = extra_paths + sys.path

# http://farmdev.com/thoughts/45/testing-google-app-engine-sites/
def setup_appserver():
    """
    Set up appserver stubs as in dev_appserver.
    """
    # these require setup_path to have been run
    from google.appengine.tools import dev_appserver
    from google.appengine.tools.dev_appserver_main import *
    option_dict = DEFAULT_ARGS.copy()
    option_dict[ARG_CLEAR_DATASTORE] = True
    
    # path to app:
    root_path = os.path.join(os.path.dirname(__file__), '..')
    (config, matcher) = dev_appserver.LoadAppConfig(root_path, {})
    # commented out stuff here that checked for SDK updates
    dev_appserver.SetupStubs(config.application, **option_dict)
