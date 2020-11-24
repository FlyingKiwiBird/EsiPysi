import asyncio
import aiohttp
import requests
import json
from .op import EsiOp
from .auth import EsiAuth
from .cache import EsiCache, DictCache
from .esisession import EsiSession
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
            retries -- Number of retries when ESI returns a retryable error, 0 disables, -1 is unlimited
            loop -- Event loop to use for asyncio
            session -- aiohttp session to use, note: loop will be useless if set with session, set the loop you want in the session instead
        """
        self.args = kwargs

        cache = kwargs.get("cache", DictCache())
        if cache is not None:
            if not issubclass(type(cache), EsiCache):
                raise TypeError("cache should be of the type EsiCache")

        session = self.args.get('session')
        if session is not None:
            if not isinstance(type(session), aiohttp.ClientSession):
                raise TypeError("session must be a aiohttp ClientSession")

        self.operations = {}
        self.data = {}
        
        r = requests.get(swagger_url)
        try:
            data = r.json()
        except:
            logger.exception("Parse error, spec written to file")
            with open('esi-spec-error.json', 'w') as esifile:
                esifile.write(r.text)
                return
        finally:
            r.close()

        self.data = data
        self.__analyze_swagger()

    def session(self) -> EsiSession:
        """
        Get a new EsiSession
        """
        session = EsiSession(self.base_url, self.operations, **self.args)
        return session

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

   