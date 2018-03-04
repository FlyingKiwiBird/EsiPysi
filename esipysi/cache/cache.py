from abc import ABC, abstractmethod
import pickle
import hashlib
import logging

logger = logging.getLogger("EsiPysi")

class EsiCache(ABC):
    """
    This is an abstract class used as a template for building caching systems
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def store(self, operation_id, operation_parameters, value, cache_time = -1):
        """
        Stores data in the cache

        :param operation_id: The id of the operation
        :param operation_parameters: parameters for the operation
        :type operation_parameters: dict
        :param value: The value to be stored in the cache
        :param cache_time: How long to store in cache (-1 is unlimited)
        :type cache_time: int (seconds)
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
    def retrieve(self, operation_id, operation_parameters, default=None):
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
        operation_dict = operation_parameters.copy()
        operation_dict["cache_operation_id"] = operation_id
        key_set = frozenset(operation_dict.items())
        hash = hashlib.md5()
        key_pickle = pickle.dumps(key_set)
        hash.update(key_pickle)
        key = hash.hexdigest()
        logger.debug("hashed {} to {}".format(key_pickle, key))
        return key