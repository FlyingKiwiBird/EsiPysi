from .cache import EsiCache

class MockCache(EsiCache):

    def __init__(self):
        """
            Chache used for testing, do not use for production as it lacks the ability to expire keys
        """
        self.cache = {}

    def store(self, operation_id, operation_parameters, value, cache_time = -1):
        key = self.get_key(operation_id, operation_parameters)

        self.cache[key] = value

    def in_cache(self, operation_id, operation_parameters):
        key = self.get_key(operation_id, operation_parameters)
        return key in self.cache

    def retrieve(self, operation_id, operation_parameters, default=None):
        key = self.get_key(operation_id, operation_parameters)

        return self.cache.get(key)