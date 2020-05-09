import aiounittest
import asyncio
from esipysi import EsiPysi
from esipysi.cache import MockCache
import datetime

class CacheTests(aiounittest.AsyncTestCase):

    async def test_simple_op(self):
        cache = MockCache()
        esi = EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test", cache=cache)
        await esi.start_session()
        op_id = "get_search"
        data = {"categories" : "character", "search" : "Flying Kiwi Sertan"}
        op = esi.get_operation(op_id)
        await op.execute(**data)
        self.assertTrue(cache.in_cache(op_id, data))
        await esi.stop_session()

    async def test_cached_list_op(self):
        cache = MockCache()
        esi = EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test", cache=cache)
        await esi.start_session()
        op_id = "post_universe_names"
        data = {"ids":[30000142, 30002693]}
        op = esi.get_operation(op_id)
        await op.execute(**data)
        self.assertTrue(cache.in_cache(op_id, data))
        await esi.stop_session()

        
    async def test_cache_retrival(self):
        cache = MockCache()
        esi = EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test", cache=cache)
        await esi.start_session()
        op_id = "get_search"
        data = {"categories" : "character", "search" : "Flying Kiwi Sertan"}
        op = esi.get_operation(op_id)
        result = await op.execute(**data)
        result_id = result.headers.get("x-esi-request-id")
        if result_id is None:
            self.fail("No result ID in headers") 

        self.assertTrue(cache.in_cache(op_id, data))

        result2 = await op.execute(**data)
        self.assertEqual(result_id, result2.headers.get("x-esi-request-id"))
        self.assertEqual(result2.json(), {'character': [95095106]})
        await esi.stop_session()
