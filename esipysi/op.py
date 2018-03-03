
import requests
import re
import urllib
import json
from urllib.error import HTTPError
from json.decoder import JSONDecodeError
from .cache.cache import EsiCache
from .auth import EsiAuth
import logging

logger = logging.getLogger("EsiPysi")

class EsiOp():
    """ A class to handle operations of the ESI api """
    def __init__(self, operation, base_url, **kwargs):
        """
        Initialize the class - this should only be done through an EsiPysi class object

        :param operation: A dict with the modified swagger structure that defines the operation
        :type operation: dict
        :param base_url: url to the base endpoint
        :type base_url: string (url)
        :param: user_agent - User agent to use when interacting with ESI
        :param: cache - EsiCache to use
        """
        self.__operation = operation
        self.__path = operation.get("path")
        self.__verb = operation.get("verb")
        self.__parameters = operation.get("parameters")
        self.__operation_id = operation.get("operationId")
        self.__base_url = base_url
        self.__cached_seconds = operation.get("x-cached-seconds", -1)
        self.user_agent = kwargs.get("user_agent")
        self.cache = kwargs.get("cache")
        auth_args = kwargs.get("auth")
        self.auth = None
        self.set_auth(auth_args)

        self.use_cache = False
        if self.cache is not None:
            if not issubclass(EsiCache, type(self.cache)):
                ValueError("cache should be of the type EsiCache")
            self.use_cache = True

    def set_auth(self, esiauth):
        """
        Set the authorization for this operation

        :param esiauth: An EsiAuth object which contains the authorization info
        :type esiauth: EsiAuth
        """
        if not issubclass(EsiAuth, type(esiauth)):
            ValueError("esiauth should be of the type EsiAuth")
        
        self.auth = esiauth

    def execute(self, parameters, raw=False):
        """
        Call the ESI API and retrieve the data

        :param parameters: A key-value pair dict with the parameters for the API operation
        :param raw: If True, return the raw text and do not parse into a dict

        :return: The API response
        :rtype: dict (if raw is True, a string)
        """
        if self.use_cache:
            value = self.cache.retrieve(self.__operation_id, parameters)
            if value is not None:
                result = self.__get_value(value, raw)
                if result is not None:
                    return result


        url = self.__base_url + self.__path
        #Handle parameters
        for name, param in self.__parameters.items():
            required = param.get("required", False)
            if required:
                if name not in parameters:
                    raise ValueError("'{}' is a required parameter".format(name))

        data_parameters = {}

        for key, value in parameters.items():
            if key not in self.__parameters:
                raise ValueError("'{}' is not a valid parameter".format(key))
            param_info = self.__parameters.get(key)
            #Handle path parameters
            if param_info.get("in") == "path":
                escaped_value = urllib.parse.quote(str(value))
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
        logger.error("Calling '{}' with data '{}' using HTTP {}".format(url, data_parameters, self.__verb.upper()))

        if self.__verb.lower() == "get":
            r = requests.get(url, params=data_parameters, headers=headers)
        elif self.__verb.lower() == "post":
            r = requests.post(url, data=data_parameters, headers=headers)
        elif self.__verb.lower() == "put":
            r = requests.put(url, data=data_parameters, headers=headers)
        elif self.__verb.lower() == "delete":
            r = requests.delete(url, data=data_parameters, headers=headers)

        if r.status_code != 200:
            raise HTTPError(url, r.status_code, r.text, headers, None)

        if self.use_cache:
            self.cache.store(self.__operation_id, parameters, r.text, self.__cached_seconds)
        
        return self.__get_value(r.text, raw)

    def __get_value(self, text, raw):
        if raw:
            return text
        try:
            json_data = json.loads(text)
        except JSONDecodeError:
            return None
        return json_data


    def __str__(self):
        return self.__operation_id
        