quickkvs
==========

Python simple key value store with in-memory, MongoDB and Redis backends. 

## Use

Here's a typical setup:

    from quickkvs import KeyValueStore, MongoBackend

    cache = KeyValueStore(backend=MongoBackend, **mongo_settings)

    # set some data that expires in 200 seconds
    cache.set("mykeyxyz", {'some': 'data'}, expires=200)

    result = cache.get("mykeyxyz")

## Installation

Mongo backend requires [PyMongo](http://api.mongodb.org/python/current/)
Redis backend requires [redis-py](https://github.com/andymccurdy/redis-py)


## Reference


## Credits


