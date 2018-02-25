import datetime
import requests
import base64
from urllib.error import HTTPError
import logging

logger = logging.getLogger("EsiPysi")

class EsiAuth():

    """
    Keeps track of authorization information, pass to an EsiOp to authorize
    """
    def __init__(self, client_id, client_secret, access_token, refresh_token, expires_at):
        """
        Sets up the authorization

        Parameters
        ----------
        client_id : str
            Eve 3rd party app client id
        client_secret : str
            Eve 3rd part app client secret
        access_token : str
            Access token from Eve SSO
        refrest_token : str
            Refresh token from Eve SSO
        expires_at : datetime
            When the token expires in UTC (Note: You will need to convert this to a datetime from the seconds CCP provides) 
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at

        key_secret = '{}:{}'.format(client_id, client_secret).encode('ascii')
        b64_encoded_key = base64.b64encode(key_secret)
        self.basic_auth = b64_encoded_key.decode('ascii')

    def authorize(self):
        """
        Returns the access token to be used in authorizations

        Returns
        ----------
        access_token : str
            Used in authorization header for ESI calls
        """
        if(self.expires_at <= datetime.datetime.utcnow()):
            self.__refresh()
        return self.access_token

    def __refresh(self):
        url = "https://login.eveonline.com/oauth/token"
        headers = {"Authorization" : "Basic {}".format(self.basic_auth), "Content-Type": "application/x-www-form-urlencoded"}
        data = {"grant_type":"refresh_token","refresh_token": self.refresh_token}
        r = requests.post(url, headers=headers, data=data)

        if r.status_code != 200:
            raise HTTPError(url, r.status_code, r.text, headers, None)

        result = r.json()
        self.access_token = result.get("access_token")
        self.refresh_token = result.get("refresh_token") #*Should* be the same but let's grab it anyway
        expires_in = int(result.get("expires_in", "0"))
        self.expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds = expires_in)
        



        