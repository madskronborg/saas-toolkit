import redis.asyncio as redis
from kitman.conf import settings


class Redis(redis.Redis):
    pass


class Sentinel(redis.Sentinel):
    pass
