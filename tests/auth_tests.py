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
        result = op.json(character_id=ai.character_id)
        print(result)

    def test_auth_verify(self):
        ai = AuthInfo()
        auth = EsiAuth(ai.client_id, ai.client_secret, ai.access_token, ai.refresh_token,  datetime.datetime(1970,1,1))
        result = auth.verify()
        print(result)

    def test_auth_verify_refresh_only(self):
        ai = AuthInfo()
        auth = EsiAuth.from_refresh_token(ai.client_id, ai.client_secret, ai.refresh_token)
        result = auth.verify()
        print(result)