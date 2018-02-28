import requests
import json
from .op import EsiOp
from .auth import EsiAuth
from .cache.cache import EsiCache
import logging

logger = logging.getLogger("EsiPysi")

class EsiPysi():
    """
    The EsiPysi class creates "EsiOp" operations based on a provided swagger spec
    """

    def __init__(self, swagger_url, **kwargs):
        """
        Initialize the class
        
        :param swagger_url: URL to the swagger spec json
        :type swagger_url: String (url)
        :param: user_agent - the user agent that will be used for calls to ESI
        :param: cache - The optional EsiCache object to be used
        """
        self.args = kwargs

        cache = kwargs.get("cache")
        if cache is not None:
            if not issubclass(EsiCache, cache):
                ValueError("cache should be of the type EsiCache")

        self.operations = {}
        self.data = {}

        r = requests.get(swagger_url)
        data = r.json()
        self.data = data

        #Get base url
        self.base_url = "https://" + data.get("host","") + data.get("basePath", "")

        #Reformat json
        paths = data.get("paths", {})
        #each path
        for path, verbs in paths.items():
            #each http verb in a path
            for verb, operation in verbs.items():
                operation_id = operation.get("operationId")
                if operation_id is None:
                    continue
                new_op = operation.copy()
                new_op["path"] = path
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

                self.operations [operation_id] = new_op

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
        
        :param operation_id: The operation id of the API call (e.g. "get_alliances_alliance_id")

        :return: An EsiOp which is used to interact with the ESI API
        :rtype: EsiOp
        """
        operation = self.operations.get(operation_id)
        if operation is None:
            return None
        return EsiOp(operation, self.base_url, **self.args)