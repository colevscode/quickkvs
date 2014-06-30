import re

from backends import MemoryBackend, RedisBackend, MongoBackend

VALID_KEY = r'^\S*$'


class InvalidKey(Exception):
    pass


class KeyValueStore(object):
    
    def __init__(self, backend=MemoryBackend, **kwargs):
        self.validkey_re = re.compile(VALID_KEY)
        self.backend = backend(**kwargs)

    def _check_key(self, key):
        if not type(key) in [str, unicode]:
            raise TypeError
        if not self.validkey_re.match(key):
            raise InvalidKey

    def __getitem__(self, key):
        self._check_key(key)
        (value, expires) = self.backend.get_item(key)
        return value

    def get(self, key, default=None):
        self._check_key(key)
        try:
            (value, expires) = self.backend.get_item(key)
            return value
        except KeyError:
            return default

    def ttl(self, key):
        self._check_key(key)
        (value, expires) = self.backend.get_item(key)
        return expires

    def __setitem__(self, key, value):
        self._check_key(key)
        self.backend.set_item(key, value, expires=-1)

    def set(self, key, value, expires=-1):
        self._check_key(key)
        self.backend.set_item(key, value, expires)

    def __delitem__(self, key):
        self._check_key(key)
        self.backend.del_item(key)

    def __contains__(self, key):
        self._check_key(key)
        return self.backend.contains_item(key)

    def expire(self, key, seconds):
        return self.backend.expire(key, seconds)

    def cleanup(self):
        return self.backend.cleanup()

    def search(self, **kwargs):
        return self.backend.search(**kwargs)



