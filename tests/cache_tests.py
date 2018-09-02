import unittest
import asyncio
from esipysi import EsiPysi
from esipysi.cache import MockCache
import datetime

class CacheTests(unittest.TestCase):

    def test_simple_op(self):
        loop = asyncio.get_event_loop()
        cache = MockCache()
        esi = EsiPysi("https://esi.tech.ccp.is/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test", cache=cache)
        op_id = "get_search"
        data = {"categories" : "character", "search" : "Flying Kiwi Sertan"}
        op = esi.get_operation(op_id)
        result = loop.run_until_complete(op.json(**data))

        self.assertTrue(cache.in_cache(op_id, data))

    def test_cached_list_op(self):
        loop = asyncio.get_event_loop()
        cache = MockCache()
        esi = EsiPysi("https://esi.tech.ccp.is/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test", cache=cache)
        op_id = "post_universe_names"
        data = {"ids":[30000142, 30002693]}
        op = esi.get_operation(op_id)
        result = loop.run_until_complete(op.json(**data))

        self.assertTrue(cache.in_cache(op_id, data))

        
