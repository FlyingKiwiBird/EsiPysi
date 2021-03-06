import asyncio
import aiohttp
import re
import urllib
import json
from enum import Enum 
from urllib.parse import urlencode
from urllib.error import HTTPError
from json.decoder import JSONDecodeError

from .cache.cache import EsiCache
from .auth import EsiAuth
from .esiresponse import EsiResponse

import logging

logger = logging.getLogger("EsiPysi")

class EsiOp(object):
    """ A class to handle operations of the ESI api """
    def __init__(self, session, operation, base_url, **kwargs):
        """
        Initialize the class - this should only be done through an EsiPysi class object

        Arguments:
            session -- A ClientSession from aiohttp used to make ESI calls
            operation -- A dict with the modified swagger structure that defines the operation
            base_url -- url to the base endpoint
        Keyword arguments:
            user_agent -- User agent to use when interacting with ESI
            cache -- an EsiCache object to use for caching queries
            auth -- an EsiAuth object to use for authorizing the ESI call
            loop -- A asyncio event loop to use for async calls
            retries -- number of retries to attempt
        """
        self.__operation = operation
        self.__path = operation.get("path")
        self.__verb = operation.get("verb")
        self.__parameters = operation.get("parameters")
        self.__operation_id = operation.get("operationId")
        self.__base_url = base_url
        self.__cached_seconds = operation.get("x-cached-seconds", -1)
        self.__user_agent = kwargs.get("user_agent")
        self.__cache = kwargs.get("cache")
        auth_args = kwargs.get("auth")
        self.__auth = None
        self.__retries = kwargs.get("retries", 5)
        self.__session = session

        if auth_args is not None:
            self.set_auth(auth_args)

        self.__use_cache = False
        if self.__cache is not None:
            if not issubclass(type(self.__cache), EsiCache):
                raise ValueError("cache should be of the type EsiCache")
            self.__use_cache = True

    def set_auth(self, esiauth):
        """
        Set the authorization for this operation

        Arguments:
            esiauth -- An EsiAuth object which contains the authorization info
        """
        if not issubclass(type(esiauth), EsiAuth):
            raise ValueError("esiauth should be of the type EsiAuth")
        
        self.__auth = esiauth

    async def json(self, **kwargs):
        """
        LEGACY - may be depricated in the future
        Call the ESI API and retrieve the json data and decode as a dict

        Keyword arguments:
            Arguments from the ESI call
        """
        raise DeprecationWarning("This feature has been removed, use execute instead")

    async def text(self, **kwargs):
        """
        DEPRICATED - No longer used
        Call the ESI API and retrieve the result as plain text (string)

        Keyword arguments:
            Arguments from the ESI call
        """
        raise DeprecationWarning("This feature has been removed, use execute instead")

    async def raw(self, **kwargs):
        """
        DEPRICATED - No longer used
        Call the ESI API and retrieve the result as plain text (string)

        Keyword arguments:
            Arguments from the ESI call
        """
        raise DeprecationWarning("This feature has been removed, use execute instead")

    async def response(self, **kwargs):
        """
        DEPRICATED - No longer used
        Call the ESI API and retrieve the result as an EsiResponse object

        Keyword arguments:
            Arguments from the ESI call
        """
        raise DeprecationWarning("This feature has been removed, use execute instead")

    async def execute(self, **kwargs):
        """
        Keyword arguments:
            Arguments from the ESI call
        """
        return await self.__call_esi_async(**kwargs)

    async def __call_esi_async(self, **kwargs):
        tries = 0
        dont_retry = [401, 403, 404, 420]
        while tries <= self.__retries:
            tries += 1
            try:
                return await self.__call(self.__session, **kwargs)
            except HTTPError as httpEx:
                if httpEx.code in dont_retry:
                    raise
                else:
                    if tries > self.__retries:
                        raise
            except:
                if tries > self.__retries:
                    raise
            await asyncio.sleep(0.1)
            
    async def __call(self, session, **kwargs):

        cache_value = self.__cache_read(**kwargs)
        if cache_value is not None:
            return cache_value

        url = self.__base_url + self.__path
        #Handle parameters
        for name, param in self.__parameters.items():
            required = param.get("required", False)
            if required:
                if name not in kwargs:
                    raise ValueError("'{}' is a required parameter".format(name))

        body = None
        query_parameters = {}
        headers = {}
        headers["accept"] = "application/json"

        for key, value in kwargs.items():
            if key not in self.__parameters:
                raise ValueError("'{}' is not a valid parameter".format(key))
            param_info = self.__parameters.get(key)
            #Handle path parameters
            param_type = param_info.get("in")
            if param_type == "path":
                escaped_value = urllib.parse.quote(str(value))
                url = url.replace("{" + param_info.get("name") + "}", escaped_value)
            elif param_type == "query":
                query_parameters[key] = value
            elif param_type == "header":
                headers[key] = value
            elif param_type == "body":
                body = json.dumps(value)

        if self.__user_agent is not None:
            headers['User-Agent'] = self.__user_agent
        if self.__auth is not None:
            auth_code = await self.__auth.authorize()
            headers["Authorization"] = "Bearer {}".format(auth_code)
        #Call operation
        logger.info("Calling '{}' with data '{}' using HTTP {}".format(url, body, self.__verb.upper()))

        if self.__verb.lower() == "get":
            async with session.get(url, params=query_parameters, headers=headers) as resp:
                return await self.__process_response(resp, **kwargs)
        else:
            #After this I don't know WTF CCP was thinking
            if query_parameters:
                query_str = "?" + urlencode(query_parameters)
            else:
                query_str = ""
            full_url = url + query_str
            if self.__verb.lower() == "post":
                async with session.post(full_url, data=body, headers=headers) as resp:
                    return await self.__process_response(resp, **kwargs)
            elif self.__verb.lower() == "put":
                async with session.put(full_url, data=body, headers=headers) as resp:
                    return await self.__process_response(resp, **kwargs)
            elif self.__verb.lower() == "delete":
                async with session.delete(full_url, data=body, headers=headers) as resp:
                    return await self.__process_response(resp, **kwargs)
        
    async def __process_response(self, resp, **kwargs):
        text = await resp.text()
        if resp.status >= 400:
            exception = HTTPError(resp.url, resp.status, text, resp.headers.copy(), None)
            logger.exception("ESI HTTP error occured: url={}, status={}, result headers={}, text={}".format(resp.url, resp.headers.copy(), resp.status, text))
            raise exception
        
        response = EsiResponse(text, resp.headers.copy(), resp.status, resp.url, self.__operation_id, kwargs)

        if self.__use_cache:
            self.__cache.store(response)
        return response

    def __cache_read(self, **kwargs):
        if not self.__use_cache:
            return None

        if not self.__cache.in_cache(self.__operation_id, kwargs):
            return None
        
        return self.__cache.retrieve(self.__operation_id, kwargs) #TODO: Make this support async too

    def __str__(self):
        return self.__operation_id
        