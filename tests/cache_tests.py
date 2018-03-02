import unittest
from esipysi import EsiPysi
from esipysi.cache import MockCache
import datetime

class CacheTests(unittest.TestCase):

    def test_simple_op(self):
        cache = MockCache()
        esi = EsiPysi("https://esi.tech.ccp.is/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test", cache=cache)
        op_id = "get_search"
        data = {"categories" : "character", "search" : "Flying Kiwi Sertan"}
        op = esi.get_operation(op_id)
        result = op.execute(data)

        self.assertTrue(cache.in_cache(op_id, data))

        
