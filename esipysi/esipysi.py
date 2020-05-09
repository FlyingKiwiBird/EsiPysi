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
            retries -- Number of retries when ESI returns a retryable error, 0 disables, -1 is unlimited
            loop -- Event loop to use for asyncio
            session -- aiohttp session to use, note: loop will be useless if set with session, set the loop you want in the session instead
        """
        self.args = kwargs

        cache = kwargs.get("cache")
        if cache is not None:
            if not issubclass(type(cache), EsiCache):
                raise TypeError("cache should be of the type EsiCache")

        self.operations = {}
        self.data = {}

        self.__loop = self.args.get('loop')
        session= self.args.get('session')

        if self.__loop is None:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            self.__loop = loop

        self.__session = None
        if session is not None:
            if not isinstance(type(session), aiohttp.ClientSession):
                raise TypeError("session must be a aiohttp ClientSession")
            self.__session = session
        
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

    async def start_session(self):
        if self.__session is not None:
            await self.stop_session()
        if self.__loop is None:
            self.__connector = aiohttp.TCPConnector(limit=50)
            self.__session = aiohttp.ClientSession(connector=self.__connector)
        else:
            if not issubclass(type(self.__loop), asyncio.BaseEventLoop):
                raise TypeError("loop must be a asyncio Loop")
            self.__connector = aiohttp.TCPConnector(limit=50, loop = self.__loop)
            self.__session = aiohttp.ClientSession(loop = self.__loop, connector=self.__connector)


    async def stop_session(self):
        logger.info("Closing the client")
        try:
            if self.__session is not None:
                await self.__session.close()
        except:
            logger.exception("Exception occured while trying to shut down session")
        finally:
            await asyncio.sleep(0)

        self.__session = None
        self.__connector = None
        
    def stop_session_sync(self):
        logger.info("Closing the client")
        if self.__loop.is_running: 
            self.__loop.create_task(self.stop_session())
        else:
            self.__loop.run_until_complete(self.stop_session())

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
        if self.__session is None:
            raise ValueError("Session is not active, please run start_session first")
            
        operation = self.operations.get(operation_id)
        if operation is None:
            raise ValueError("Could not find an operation with the name '{}'".format(operation_id))
        return EsiOp(self.__session, operation, self.base_url, **self.args)