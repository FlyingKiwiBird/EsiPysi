import aiounittest
import asyncio
from esipysi import EsiPysi
import datetime
from urllib.error import HTTPError

class BasicTests(aiounittest.AsyncTestCase):

    async def test_simple_op(self):
        async with EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test").session() as esi:
            op = esi.get_operation("get_search")
            result = await op.execute(categories="character", search="Flying Kiwi Sertan")
            self.assertEqual(result.json(), {'character': [95095106]})

    async def test_post_op(self):
        async with EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test").session() as esi:
            op = esi.get_operation("post_universe_names")
            await op.execute(ids=[30000142, 30002693])

    async def test_text_op(self):
        async with EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test").session() as esi:
            op = esi.get_operation("get_search")
            result = await op.execute(categories="character", search="Flying Kiwi Sertan")
            self.assertEqual(result.text, "{\"character\":[95095106]}")

    async def test_404_op(self):
        async with EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test").session() as esi:
            op = esi.get_operation("get_universe_regions_region_id")
            result = await op.execute(region_id=9)
            self.assertEqual(result.status, 404)

    async def test_headers(self):
        async with EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test").session() as esi:
            op = esi.get_operation("get_search")
            result = await op.execute(categories="character", search="Flying Kiwi Sertan")
            self.assertIsNotNone(result.headers.get("x-esi-request-id"))


    
