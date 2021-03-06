from .cache import EsiCache
from esipysi.esiresponse import EsiResponse
import pickle
from datetime import datetime
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
        if not issubclass(type(redis_client), StrictRedis):
            raise ValueError("redis_client should be a StrictRedis object")

        self.redis = redis_client

    def store(self, value : EsiResponse):

        operation_id = value.operation_id
        operation_parameters = value.operation_parameters

        key = self.get_key(operation_id, operation_parameters)

        self.redis.set(key, pickle.dumps(value))

        expires_dt = value.expires()
        if expires_dt is not None:
            expires_diff = expires_dt - datetime.utcnow()
            self.redis.expire(key, expires_diff.total_seconds())            

    def in_cache(self, operation_id, operation_parameters):
        key = self.get_key(operation_id, operation_parameters)

        return self.redis.exists(key)

    def retrieve(self, operation_id, operation_parameters, default=None):
        key = self.get_key(operation_id, operation_parameters)

        value = self.redis.get(key)
        if value is None:
            return default
        
        return pickle.loads(value)

