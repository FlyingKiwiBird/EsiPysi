import unittest
from esipysi import EsiPysi
from esipysi import EsiAuth
from .auth_secret import AuthInfo
import datetime

class AuthTests(unittest.TestCase):
    
    def test_auth_op(self):
        esi = EsiPysi("https://esi.tech.ccp.is/latest/swagger.json?datasource=tranquility", user_agent="Eve Test")
        op =  esi.get_operation("get_characters_character_id_ship")
        ai = AuthInfo()
        auth = EsiAuth(ai.client_id, ai.client_secret, ai.access_token, ai.refresh_token,  datetime.datetime(1970,1,1))
        op.set_auth(auth)
        result = op.execute({"character_id":ai.character_id})
        print(result)

    def test_auth_verify(self):
        ai = AuthInfo()
        esi = EsiPysi("https://esi.tech.ccp.is/latest/swagger.json?datasource=tranquility", user_agent="Eve Test")
        auth = EsiAuth(ai.client_id, ai.client_secret, ai.access_token, ai.refresh_token,  datetime.datetime(1970,1,1))
        result = auth.verify()
        print(result)

    def test_auth_update_fleet(self):
        ai = AuthInfo()
        auth = EsiAuth(ai.client_id, ai.client_secret, ai.access_token, ai.refresh_token,  datetime.datetime(1970,1,1))
        esi = EsiPysi("https://esi.tech.ccp.is/_latest/swagger.json?datasource=tranquility", user_agent="Eve Test", auth=auth)
        op =  esi.get_operation("get_characters_character_id_fleet")
        result = op.execute({"character_id" :ai.character_id})
        fleet_id = result.get("fleet_id")
        op2 = esi.get_operation("get_fleets_fleet_id_members")
        data = {"fleet_id" : fleet_id}
        result = op2.execute(data)

        print(result)
