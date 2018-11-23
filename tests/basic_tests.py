import unittest
import asyncio
from esipysi import EsiPysi
import datetime
from urllib.error import HTTPError

class BasicTests(unittest.TestCase):

    def test_simple_op(self):
        esi = EsiPysi("https://esi.tech.ccp.is/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test")
        op = esi.get_operation("get_search")
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(op.json(categories="character", search="Flying Kiwi Sertan"))
        self.assertEqual(result, {'character': [95095106]})

    def test_post_op(self):
        esi = EsiPysi("https://esi.tech.ccp.is/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test")
        op = esi.get_operation("post_universe_names")
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(op.json(ids=[30000142, 30002693]))
        #print(result)

    def test_text_op(self):
        esi = EsiPysi("https://esi.tech.ccp.is/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test")
        op = esi.get_operation("get_search")
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(op.text(categories="character", search="Flying Kiwi Sertan"))
        self.assertEqual(result, "{\"character\":[95095106]}")

    def test_response_op(self):
        esi = EsiPysi("https://esi.tech.ccp.is/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test")
        op = esi.get_operation("get_search")
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(op.response(categories="character", search="Flying Kiwi Sertan"))
        text = loop.run_until_complete(response.json())
        self.assertEqual(text, {'character': [95095106]})

    def test_404_op(self):
        esi = EsiPysi("https://esi.tech.ccp.is/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test")
        op = esi.get_operation("get_universe_regions_region_id")
        loop = asyncio.get_event_loop()
        try:
            response = loop.run_until_complete(op.response(region_id=9))
            self.fail("Should raise exception")
        except HTTPError as ex:
            self.assertEqual(ex.code, 404)



    
