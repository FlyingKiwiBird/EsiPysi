from abc import ABC, abstractmethod
import pickle
import hashlib
import logging
import esipysi
from esipysi.esiresponse import EsiResponse

logger = logging.getLogger("EsiPysi")

class EsiCache(ABC):
    """
    This is an abstract class used as a template for building caching systems
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def store(self, value : EsiResponse):
        """
        Stores data in the cache

        :param operation_id: The id of the operation
        :param operation_parameters: parameters for the operation
        :type operation_parameters: dict
        :param value: The value to be stored in the cache
        """
        raise NotImplementedError()

    @abstractmethod
    def in_cache(self, operation_id, operation_parameters):
        """
        Check for a cache hit

        :param operation_id: The id of the operation
        :param operation_parameters: parameters for the operation
        :type operation_parameters: dict

        :return: True if stored in the cache, False otherwise
        """
        raise NotImplementedError()

    @abstractmethod
    def retrieve(self, operation_id, operation_parameters, default=None) -> EsiResponse:
        """
        Returns data in the cache

        :param operation_id: The id of the operation
        :param operation_parameters: parameters for the operation
        :type operation_parameters: dict
        :param default: A default value if not in cache (defaults to None)

        :return: stored value if in the cache, default otherwise
        """
        raise NotImplementedError()

    def get_key(self, operation_id, operation_parameters):
        """
        Returns the key used in the cache

        :param operation_id: The id of the operation
        :param operation_parameters: parameters for the operation
        :type operation_parameters: dict

        :return: The key generated to store the value in the cache
        """
        #Generate a key
        hash_dict = {}
        hash_dict["cache_operation_id"] = operation_id
        hash_dict["esipysi_version"] = esipysi.__version__
        for key, value in operation_parameters.items():
            hash_dict[key] = pickle.dumps(value)

        key_set = frozenset(hash_dict.items())
        hash = hashlib.md5()
        key_pickle = pickle.dumps(key_set)
        hash.update(key_pickle)
        key = hash.hexdigest()
        logger.debug("hashed {} to {}".format(key_pickle, key))
        return key