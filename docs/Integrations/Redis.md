# Redis

Easily integrate your service with Redis with settings management and async clients based on [redis-py](https://github.com/redis/redis-py).

The integration includes `hiredis` by default, which includes up to 10X performance improvements.

## Settings

Add support for configuring your Redis client(s) directly in your app settings with `kitman.ext.redis.RedisSettings`.

**Environment Variables**

The environment variable keys are in the format: `REDIS_<setting_key>` in uppercase.

- `REDIS_HOST` (str, default: "localhost") - The hostname of the Redis server
- `REDIS_PORT` (int, default: 6739) - The port of the Redis server
- `REDIS_DB` (str | int, default: 0) - The database of the Redis server
- `REDIS_USERNAME` (str, optional) - The username for authenticating with the Redis server
- `REDIS_PASSWORD` (str, optional) - The password for authenticating with the Redis server
- `REDIS_SSL` (bool, default: False) - Connect to Redis server over tls

For further settings, please consult `redis-py`'s documentation. Any argument or keyword argument that is accepted by the `__init__` method of the `redis.Redis` client is applicable.

**Example**

```py
# in conf.py
from kitman.fastapi.conf import AppSettings
from kitman.ext import redis

class Settings(AppSettings, redis.RedisSettings):
    pass

```

## Usage

The async Redis client class can be imported from `kitman.ext.redis.Redis`.<br>
It is a wrapper around `redis-py`'s `redis.asyncio.Redis` client. Please consult `redis-py`'s documentation for further usage documentation.

**Example**

```py

from app.conf import settings
from kitman.ext import redis

r = redis.Redis(**settings.get_redis_options())

async def get_key():

    value = await r.get("my-key")

    return value

# Or with custom options. E.g. using db=1 instead of db=0

r_db1 = redis.Redis(**settings.get_redis_options(db=1))

async def get_key_from_db_1():

    value = await r_db1.get("my-key")

    return value

```
