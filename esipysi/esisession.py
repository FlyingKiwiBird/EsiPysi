
import aiohttp
import logging
import asyncio
from .op import EsiOp

logger = logging.getLogger("EsiPysi")

class EsiSession(object):
    def __init__(self, base_url, operations,  **kwargs):
        self.__loop = kwargs.get("loop")
        self.__session = kwargs.get("session")
        self.__args = kwargs
        self.__operations = operations
        self.__base_url = base_url

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.stop()

    async def start(self):
        if self.__session is None:
            if self.__loop is None:
                self.__connector = aiohttp.TCPConnector(limit=50)
                self.__session = aiohttp.ClientSession(connector=self.__connector)
            else:
                if not issubclass(type(self.__loop), asyncio.BaseEventLoop):
                    raise TypeError("loop must be a asyncio Loop")
                self.__connector = aiohttp.TCPConnector(limit=50, loop = self.__loop)
                self.__session = aiohttp.ClientSession(loop = self.__loop, connector=self.__connector)

    def get_operation(self, operation_id):
        """
        Get an ESI operation from it's id

        Arguments:
            operation_id -- The id of the swagger operation
        """
        if self.__session is None:
            raise ValueError("Session is None")

        if self.__session.closed:
            raise RuntimeError("Session is closed")
            
        operation = self.__operations.get(operation_id)
        if operation is None:
            raise ValueError("Could not find an operation with the name '{}'".format(operation_id))
        return EsiOp(self.__session, operation, self.__base_url, **self.__args)

    async def stop(self):
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

    

    