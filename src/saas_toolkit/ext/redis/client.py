import redis.asyncio as redis
from saas_toolkit.conf import SETTINGS


class Redis(redis.Redis):
    pass


class Sentinel(redis.Sentinel):
    pass
