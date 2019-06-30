import unittest
import asyncio
from esipysi import EsiPysi
import datetime
from urllib.error import HTTPError

class BasicTests(unittest.TestCase):

    def test_simple_op(self):
        esi = EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test")
        op = esi.get_operation("get_search")
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(op.execute(categories="character", search="Flying Kiwi Sertan"))
        self.assertEqual(result.json(), {'character': [95095106]})
        esi.close()

    def test_post_op(self):
        esi = EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test")
        op = esi.get_operation("post_universe_names")
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(op.execute(ids=[30000142, 30002693]))
        esi.close()

    def test_text_op(self):
        esi = EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test")
        op = esi.get_operation("get_search")
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(op.execute(categories="character", search="Flying Kiwi Sertan"))
        self.assertEqual(result.text, "{\"character\":[95095106]}")
        esi.close()

    def test_404_op(self):
        esi = EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test")
        op = esi.get_operation("get_universe_regions_region_id")
        loop = asyncio.get_event_loop()
        try:
            response = loop.run_until_complete(op.execute(region_id=9))
            self.fail("Should raise exception")
        except HTTPError as ex:
            self.assertEqual(ex.code, 404)
        finally:
            esi.close()

    def test_headers(self):
        esi = EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test")
        op = esi.get_operation("get_search")
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(op.execute(categories="character", search="Flying Kiwi Sertan"))
        self.assertIsNotNone(result.headers.get("x-esi-request-id"))
        esi.close()


    
