import datetime
import asyncio
import aiohttp
import requests
import base64
from urllib.error import HTTPError
import logging

logger = logging.getLogger("EsiPysi")

class EsiAuth(object):

    """
    Keeps track of authorization information, pass to an EsiOp to authorize
    """
    def __init__(self, client_id, client_secret, access_token, refresh_token, expires_at, login_server="login.eveonline.com", loop=None):
        """
        Sets up the authorization

        Arguments:
            client_id -- Eve 3rd party developer client id
            client_secret -- The secret key to go with the client_id
            access_token -- Access token from Eve SSO
            refresh_token -- Refresh token from Eve SSO
            expires_at -- a UTC datetime of when the access token will expire
            login_server -- The Eve SSO login server (defaults to tranquility login server)
            loop -- An asyncio loop for esi calls (defaults to the current loop)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at
        if loop is None:
            self.loop = None
        else:
            if isinstance(loop, asyncio.BaseEventLoop):
               self.loop = loop
            else:
                raise TypeError("Loop argument must either be 'None' or impliment BaseEventLoop") 

        self.__login_server = login_server

        key_secret = '{}:{}'.format(client_id, client_secret).encode('ascii')
        b64_encoded_key = base64.b64encode(key_secret)
        self.basic_auth = b64_encoded_key.decode('ascii')

    @classmethod
    async def from_authorization_code(cls, client_id, client_secret, authorization_code, login_server="login.eveonline.com"):
        esi_auth = cls(client_id, client_secret, None, None, None, login_server)
        await esi_auth.get_new_token(authorization_code)
        return esi_auth

    @classmethod 
    async def from_refresh_token(cls, client_id, client_secret, refresh_token, login_server="login.eveonline.com"):
        esi_auth = cls(client_id, client_secret, None, refresh_token, None, login_server)
        await esi_auth.get_new_token()
        return esi_auth

    async def authorize(self):
        """
        Returns the access token to be used in authorizations.  This function is reccomended over 
        getting the access token from the properties because it checks if the token is expired.

        Returns:
            Access token to ESI
        """
        if(self.is_expired()):
            await self.get_new_token()
        return self.access_token

    def is_expired(self, offset=0):
        """
        Determines if the access token is expired

        Arguments:
            offset -- seconds to shift the check, e.g. with an offset of 30 if the token is still valid for 29 seconds the check will fail (default: 0)
        
        Returns:
            True if token is valid, False otherwise
        """
        if self.expires_at is None:
            return True
        offset_delta = datetime.timedelta(seconds=offset)
        return (self.expires_at + offset_delta) <= datetime.datetime.utcnow()

    async def get_new_token(self, authorization_code = None):
        """
        Acquire a new token using the refresh token or provided authorization_code

        Arguments:
            authorization_code -- The code from the Authorization Code Grant of Eve SSO, only required if a refresh token is not avaliable (default: None)
        """    
        if self.refresh_token is not None:
            data = {"grant_type":"refresh_token","refresh_token": self.refresh_token}
        elif authorization_code is not None:
            data = {"grant_type":"authorization_code","code": authorization_code}
        else:
            raise ValueError("Either refresh_token or authorization_code is required")

        url = "https://" + self.__login_server + "/oauth/token"
        headers = {"Authorization" : "Basic {}".format(self.basic_auth), "Content-Type": "application/x-www-form-urlencoded"}


        async with aiohttp.ClientSession(loop=self.loop) as session:
            async with session.post(url, headers=headers, data=data) as resp:
                text = await resp.text()
                if resp.status >= 400:
                    raise HTTPError(url, resp.status, text, headers, None)

                result = await resp.json()
                self.access_token = result.get("access_token")
                self.refresh_token = result.get("refresh_token") #*Should* be the same but let's grab it anyway
                expires_in = int(result.get("expires_in", "0"))
                self.expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds = expires_in)

    async def verify(self, raw = False):
        """
        Retrieve details about the authorized user / token
        
        Arguments:
            raw -- Output directly as text instead of parsing the JSON

        Returns:
            Results of the verify SSO call
        """

        url = "https://" + self.__login_server + "/oauth/verify"
        auth = await self.authorize()
        headers = {"Authorization" : "Bearer {}".format(auth)}
        async with aiohttp.ClientSession(loop=self.loop) as session:
            async with session.get(url, headers=headers) as resp:
                text = await resp.text()
                if resp.status >= 400:
                    raise HTTPError(url, resp.status, text, headers, None)

                if raw:
                    return text
                return await resp.json()
        


        



        