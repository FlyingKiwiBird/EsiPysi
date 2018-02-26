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
    def __init__(self, client_id, client_secret, access_token, refresh_token, expires_at, login_server="login.eveonline.com"):
        """
        Sets up the authorization

        :param client_id: Eve 3rd party app client id
        :param client_secret: Eve 3rd part app client secret
        :param access_token: Access token from Eve SSO
        :param refrest_token: Refresh token from Eve SSO
        :param expires_at: When the token expires in UTC (Note: You will need to convert this to a datetime from the seconds CCP provides)
        :type expires_at: datetime
        :param login_server: (optional) change the login server from the default server
        :type login_server: string (url)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at

        self.__login_server = login_server

        key_secret = '{}:{}'.format(client_id, client_secret).encode('ascii')
        b64_encoded_key = base64.b64encode(key_secret)
        self.basic_auth = b64_encoded_key.decode('ascii')

    def authorize(self):
        """
        Returns the access token to be used in authorizations.  This function is reccomended over 
        getting the access token from the properties because it checks if the token is expired.

        :return: a string that is the access token 
        """
        if(self.is_expired()):
            self.get_new_token()
        return self.access_token

    def is_expired(self, offset=0):
        """
        Determines if the access token is expired

        :param offset: offset in seconds to test (e.g. if you want to know if the token will be valid in 30 seconds, offset=30)
        :type offset: int (seconds)

        :return: The validity of the access token
        :rtype: boolean
        """
        offset_delta = datetime.timedelta(seconds=offset)
        return (self.expires_at + offset_delta) <= datetime.datetime.utcnow()

    def get_new_token(self):
        """
        Acquire a new token using the provided refresh token
        """
        url = "https://" + self.__login_server + "/oauth/token"
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

    def verify(self, raw = False):
        """
        Retrieve details about the authorized user / token
        :param raw: If True, return the raw text and do not parse into a dict

        :return: Details about the authorized user / token
        :rtype: dict (if raw is True, a string)
        """

        url = "https://" + self.__login_server + "/oauth/verify"
        headers = {"Authorization" : "Basic {}".format(self.basic_auth)}
        r = requests.post(url, headers=headers)

        if r.status_code != 200:
            raise HTTPError(url, r.status_code, r.text, headers, None)

        if raw:
            return r.text
        return r.json()
        


        



        