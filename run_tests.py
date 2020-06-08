from tests.basic_tests import BasicTests
#from tests.auth_tests import AuthTests
from tests.cache_tests import CacheTests
import unittest
import logging

ep_log = logging.getLogger("EsiPysi")
ep_log.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
ep_log.addHandler(ch)

unittest.main()