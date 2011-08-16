import unittest

import setup
setup.setup_path()
setup.setup_appserver()

from test_provider import *

unittest.main()
