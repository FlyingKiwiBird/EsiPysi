import asyncio
import aiohttp
import requests
import json
from .op import EsiOp
from .auth import EsiAuth
from .cache.cache import EsiCache
import logging

logger = logging.getLogger("EsiPysi")

class EsiPysi(object):
    """
    The EsiPysi class creates "EsiOp" operations based on a provided swagger spec
    """

    def __init__(self, swagger_url, **kwargs):
        """
        Initialize the class

        Arguments:
            swagger_url -- Url to the swagger spec

        Keyword arguments:
            user_agent -- user agent to send with ESI calls
            cache -- EsiCache object to use for caching
            auth -- EsiAuth to use for authorized calls to ESI
            loop -- Event loop to use for asyncio
        """
        self.args = kwargs
        self.__is_ready = False
        self.__loading = False

        cache = kwargs.get("cache")
        if cache is not None:
            if not issubclass(EsiCache, type(cache)):
                TypeError("cache should be of the type EsiCache")

        self.operations = {}
        self.data = {}
        
        r = requests.get(swagger_url)
        data = r.json()
            
        self.data = data
        self.__analyze_swagger()
        self.__is_ready = True


    def __analyze_swagger(self):
        #Get base url
        self.base_url = "https://" + self.data.get("host","") + self.data.get("basePath", "")

        #Reformat json
        paths = self.data.get("paths", {})
        #each path
        for route, verbs in paths.items():
            #each http verb in a path
            for verb, operation in verbs.items():
                operation_id = operation.get("operationId")
                if operation_id is None:
                    continue
                new_op = operation.copy()
                new_op["path"] = route
                new_op["verb"] = verb

                #Handle parameter refs
                params = operation.get("parameters")
                new_op["parameters"] = {}
                for param in params:
                    path = param.get("$ref")
                    if path is None:
                        param_details = param.copy()
                    else:
                        param_details = self.__get_ref(path)
                    param_name = param_details.get("name")
                    new_op["parameters"][param_name] = param_details

                self.operations[operation_id] = new_op

    def __get_ref(self, path):
        path_split = path.split("/")
        if path_split[0] != "#":
            #Unsupported
            return None
        ref = self.data
        for i in range(1, len(path_split)):
            ref = ref.get(path_split[i], {})

        return ref

    def get_operation(self, operation_id):
        """
        Get an ESI operation from it's id

        Arguments:
            operation_id -- The id of the swagger operation
        """
        operation = self.operations.get(operation_id)
        if operation is None:
            return None
        return EsiOp(operation, self.base_url, **self.args)