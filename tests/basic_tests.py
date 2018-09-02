import unittest
import asyncio
from esipysi import EsiPysi
import datetime

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


    
