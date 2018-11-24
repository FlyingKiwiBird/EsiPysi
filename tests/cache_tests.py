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
        result = loop.run_until_complete(op.execute(**data))

        self.assertTrue(cache.in_cache(op_id, data))

    def test_cached_list_op(self):
        loop = asyncio.get_event_loop()
        cache = MockCache()
        esi = EsiPysi("https://esi.tech.ccp.is/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test", cache=cache)
        op_id = "post_universe_names"
        data = {"ids":[30000142, 30002693]}
        op = esi.get_operation(op_id)
        result = loop.run_until_complete(op.execute(**data))

        self.assertTrue(cache.in_cache(op_id, data))

        
    def test_cache_retrival(self):
        loop = asyncio.get_event_loop()
        cache = MockCache()
        esi = EsiPysi("https://esi.tech.ccp.is/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test", cache=cache)
        op_id = "get_search"
        data = {"categories" : "character", "search" : "Flying Kiwi Sertan"}
        op = esi.get_operation(op_id)
        result = loop.run_until_complete(op.execute(**data))
        result_id = result.headers.get("x-esi-request-id")
        if result_id is None:
            self.fail("No result ID in headers") 

        self.assertTrue(cache.in_cache(op_id, data))

        result2 = loop.run_until_complete(op.execute(**data))
        self.assertEqual(result_id, result2.headers.get("x-esi-request-id"))
        self.assertEqual(result2.json(), {'character': [95095106]})
