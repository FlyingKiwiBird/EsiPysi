import unittest
from esipysi.esipysi import EsiPysi
from esipysi.esiauth import EsiAuth
import datetime

class BasicTests(unittest.TestCase):

    def test_simple_op(self):
        esi = EsiPysi("https://esi.tech.ccp.is/latest/swagger.json?datasource=tranquility", user_agent="Eve Test")
        op = esi.get_operation("get_search")
        result = op.execute({"categories" : "character", "search" : "Flying Kiwi Sertan"})
        self.assertEqual(result, {'character': [95095106]})

if __name__ == '__main__':
    unittest.main()