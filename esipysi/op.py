
import requests
import re
import urllib
from urllib.error import HTTPError
import logging

logger = logging.getLogger("EsiPysi")

class EsiOp():
    """ A class to handle operations of the ESI api """
    def __init__(self, operation, base_url, user_agent):
        """
        Initialize the class - this should only be done through an EsiPysi class object

        :param operation: A dict with the modified swagger structure that defines the operation
        :type operation: dict
        :param base_url: url to the base endpoint
        :type base_url: string (url)
        :param user_agent: User agent to use when interacting with ESI 
        """
        self.operation = operation
        self.path = operation.get("path")
        self.verb = operation.get("verb")
        self.parameters = operation.get("parameters")
        self.base_url = base_url
        self.user_agent = user_agent
        self.auth = None

    def set_auth(self, esiauth):
        """
        Set the authorization for this operation

        :param esiauth: An EsiAuth object which contains the authorization info
        :type esiauth: EsiAuth
        """
        self.auth = esiauth

    def execute(self, parameters, raw=False):
        """
        Call the ESI API and retrieve the data

        :param parameters: A key-value pair dict with the parameters for the API operation
        :param raw: If True, return the raw text and do not parse into a dict

        :return: The API response
        :rtype: dict (if raw is True, a string)
        """
        url = self.base_url + self.path
        #Handle parameters
        for name, param in self.parameters.items():
            required = param.get("required", False)
            if required:
                if name not in parameters:
                    raise ValueError("'{}' is a required parameter".format(name))

        data_parameters = {}

        for key, value in parameters.items():
            if key not in self.parameters:
                raise ValueError("'{}' is not a valid parameter".format(key))
            param_info = self.parameters.get(key)
            #Handle path parameters
            if param_info.get("in") == "path":
                escaped_value = urllib.parse.quote(value)
                url = url.replace("{" + param_info.get("name") + "}", escaped_value)
            else:
                data_parameters[key] = value

        headers = {}
        if self.user_agent is not None:
            headers['User-Agent'] = self.user_agent
        if self.auth is not None:
            auth_code = self.auth.authorize()
            headers["Authorization"] = "Bearer {}".format(auth_code)
        #Call operation
        if self.verb == "get":
            r = requests.get(url, params=data_parameters, headers=headers)
        elif self.verb == "post":
            r = requests.post(url, data=data_parameters, headers=headers)
        elif self.verb == "put":
            r = requests.put(url, data=data_parameters, headers=headers)
        elif self.verb == "delete":
            r = requests.delete(url, data=data_parameters, headers=headers)

        if r.status_code != 200:
            raise HTTPError(url, r.status_code, r.text, headers, None)
        if(raw):
            return r.text
        return r.json()
        