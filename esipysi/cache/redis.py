from .cache import EsiCache
import pickle
try:
    from redis import StrictRedis
except ImportError:
    #Redis not installed
    pass


class RedisCache(EsiCache):

    def __init__(self, redis_client):
        """
        :param redis_client: The redis client to store the cache in
        :type redis_client: StrictRedis
        """
        if not issubclass(StrictRedis, type(redis_client)):
            raise ValueError("redis_client should be a StrictRedis object")

        self.redis = redis_client

    def store(self, operation_id, operation_parameters, value, cache_time = -1):
        key = self.get_key(operation_id, operation_parameters)

        self.redis.set(key, pickle.dumps(value))
        if cache_time != -1:
            self.redis.expire(key, cache_time)

    def in_cache(self, operation_id, operation_parameters):
        key = self.get_key(operation_id, operation_parameters)

        return self.redis.exists(key)

    def retrieve(self, operation_id, operation_parameters, default=None):
        key = self.get_key(operation_id, operation_parameters)

        value = self.redis.get(key)
        if value is None:
            return default
        return pickle.loads(value)

