import redis.asyncio as redis
from kitman.conf import SETTINGS


class Redis(redis.Redis):
    pass


class Sentinel(redis.Sentinel):
    pass
