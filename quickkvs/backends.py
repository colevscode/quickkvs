import json
import time

class ExpirationMixin(object):

    def _calc_ttl(self, item):
        if item['expires'] < 0: return -1 # never expires
        ttl = item['expires'] - time.clock()
        return 0 if ttl < 0 else ttl

    def _set_expires(self, item, expires):
        item['expires'] = time.clock() + expires if expires > 0 else -1


class MemoryBackend(ExpirationMixin):

    def __init__(self, dictionary=None):
        self._dict = dictionary or {}

    def get_item(self, key):
        item = self._dict.get(key)
        if not item:
            raise KeyError
        ttl = self._calc_ttl(item)
        if ttl == 0:
            self.del_item(key)
            raise KeyError
        return item['value'], ttl

    def set_item(self, key, value, expires):
        item = {'value': value}
        self._set_expires(item, expires)
        self._dict[key] = item

    def del_item(self, key):
        del self._dict[key]

    def contains_item(self, key):
        self.cleanup()
        return key in self._dict.keys()

    def expire(self, key, seconds):
        item, exp = self.get_item(key)
        self._set_expires(item, seconds)

    def cleanup(self):
        map = lambda x: self._calc_obj_ttl(x)
        red = lambda x: x == -1 or x > 0
        self._dict = dict((k, v) for k, v in self._dict.iteritems() if red(map(v)))

    def search(self, **kwargs):
        raise NotImplemented


class MongoBackend(ExpirationMixin):

    def __init__(self, mongo=None, host="localhost:27017", user='', passwd='', 
                 db="_mongo_token_store", col="default_token_store"):
        from pymongo import MongoClient
        if not mongo:
            auth = '%s:%s@' % (user, passwd) if user else ''
            uri  = 'mongodb://' + auth + host
            self._mongo = MongoClient(host=uri)
        else:
            self._mongo = mongo
        self._db = db
        self._col = col

    def get_item(self, key):
        col = self._mongo[self._db][self._col]
        item = col.find_one({'_id':key})
        if not item:
            raise KeyError
        ttl = self._calc_ttl(item)
        if ttl == 0:
            self.del_item(key)
            raise KeyError
        return item['value'], ttl

    def set_item(self, key, value, expires):
        col = self._mongo[self._db][self._col]
        item = {'_id':key, 'value': value}
        self._set_expires(item, expires)
        col.update({'_id':key}, item, upsert=True)

    def del_item(self, key):
        col = self._mongo[self._db][self._col]
        col.remove({'_id':key})

    def contains_item(self, key):
        col = self._mongo[self._db][self._col]
        self.cleanup(col=col)
        return col.count({'_id':key}) > 0

    def expire(self, key, seconds):
        col = self._mongo[self._db][self._col]
        col.update({'_id':key}, {'$set': {
            'expires': time.clock() + seconds if seconds > 0 else -1
        }})

    def cleanup(self, col=None):
        col = col or self._mongo[self._db][self._col]
        col.remove({'expires': {'$lt': time.clock()}})

    def search(self, *args, **kwargs):
        '''
        Three possible ways to invoke:

        search(arg) - looks for values that match the arg
        search(*args) - looks for values that match any arg
        search(**kwargs) -
            assumes that the values are objects. Finds all objects
            for which each kwarg matches a property

        If both args and kwargs are passed, kwargs will be ignored
        ''' 
        col = self._mongo[self._db][self._col]
        self.cleanup(col=col)
        if len(args) == 1:
            query = {'value': args[0]}
        elif len(args) > 1:
            query = {'value': {'$in': args}}
        else:
            query = dict((u'value.'+unicode(k), unicode(v)) for k, v in kwargs)
        results = col.find(query)
        return dict((item['_id'], item['value']) for item in results)


class RedisBackend(object):

    def __init__(self, redis=None, host="localhost", port=6379, pw=None, db=0):
        from redis import StrictRedis
        self._redis = redis or StrictRedis(host=host, port=port, password=pw, db=db)

    def _calc_ttl(self, item):
        return self._redis.ttl(item)

    def get_item(self, key):
        item = self._redis.get(key)
        if not item:
            raise KeyError
        ttl = self._calc_ttl(item)
        return json.loads(unicode(item, "utf-8")), ttl

    def set_item(self, key, value, expires):
        data = unicode(json.dumps(value)).encode("utf-8")
        self._redis.set(key, data)
        if expires >= 0:
            self._redis.expire(key, expires)

    def del_item(self, key):
        self._redis.delete(key)

    def contains_item(self, key):
        return self._redis.exists(key)

    def expire(self, key, seconds):
        self._redis.expire(key, seconds)

    def cleanup(self):
        pass

    def search(self, **kwargs):
        raise NotImplemented