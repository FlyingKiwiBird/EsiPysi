from .cache import EsiCache
from esipysi.esiresponse import EsiResponse
from datetime import datetime, timedelta
import pytz

cache_clean_time = timedelta(minutes=10)

class DictCache(EsiCache):

    def __init__(self):
        self.__cache = {}
        self.__next_clean = datetime.utcnow() + cache_clean_time

    def store(self, value : EsiResponse):

        operation_id = value.operation_id
        operation_parameters = value.operation_parameters
        key = self.get_key(operation_id, operation_parameters)
        expires_dt = value.expires()
        
        if expires_dt is None:
            return

        cache_item = {"item" : value, "expires" : expires_dt}
        self.__cache[key] = cache_item

        self.__clean()

    def in_cache(self, operation_id, operation_parameters):
        key = self.get_key(operation_id, operation_parameters)
        item = self.__cache.get(key)

        if item is None:
            return False

        if self.__is_expired(item):
            self.__cache.pop(key) # Remove the expired key
            return False

        return True

    def retrieve(self, operation_id, operation_parameters, default=None):
         key = self.get_key(operation_id, operation_parameters)

         if self.in_cache(operation_id, operation_parameters):
             entry = self.__cache.get(key)
             return entry.get("item")

    def __is_expired(self, item):
        expires_at = item.get("expires")

        if expires_at is None:
            return False

        if expires_at < self.__utcnow():
            return True

        return False

    def __clean(self):
        if self.__next_clean > datetime.utcnow():
            return

        self.__next_clean = datetime.utcnow() + cache_clean_time

        for key, entry in self.__cache:
            if self.__is_expired(entry):
                self.__cache.pop(key) # Remove the expired key

    def __utcnow(self):
        return datetime.utcnow().replace(tzinfo=pytz.utc)

        

        

