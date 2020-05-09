import aiounittest
import asyncio
from esipysi import EsiPysi
import datetime
from urllib.error import HTTPError

class BasicTests(aiounittest.AsyncTestCase):

    async def test_simple_op(self):
        esi = EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test")
        await esi.start_session()
        op = esi.get_operation("get_search")
        result = await op.execute(categories="character", search="Flying Kiwi Sertan")
        self.assertEqual(result.json(), {'character': [95095106]})
        await esi.stop_session()

    async def test_post_op(self):
        esi = EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test")
        await esi.start_session()
        op = esi.get_operation("post_universe_names")
        await op.execute(ids=[30000142, 30002693])
        await esi.stop_session()

    async def test_text_op(self):
        esi = EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test")
        await esi.start_session()
        op = esi.get_operation("get_search")
        loop = asyncio.get_event_loop()
        result = await op.execute(categories="character", search="Flying Kiwi Sertan")
        self.assertEqual(result.text, "{\"character\":[95095106]}")
        await esi.stop_session()

    async def test_404_op(self):
        esi = EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test")
        await esi.start_session()
        op = esi.get_operation("get_universe_regions_region_id")
        loop = asyncio.get_event_loop()
        try:
            response = await op.execute(region_id=9)
            self.fail("Should raise exception")
        except HTTPError as ex:
            self.assertEqual(ex.code, 404)
            print(ex)
        finally:
            await esi.stop_session()

    async def test_headers(self):
        esi = EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test")
        await esi.start_session()
        op = esi.get_operation("get_search")
        loop = asyncio.get_event_loop()
        result = await op.execute(categories="character", search="Flying Kiwi Sertan")
        self.assertIsNotNone(result.headers.get("x-esi-request-id"))
        await esi.stop_session()


    
