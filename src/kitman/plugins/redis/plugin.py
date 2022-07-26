from kitman import Plugin, Kitman
from .client import Redis
from .conf import RedisConf


class RedisPlugin(Plugin):
    name = "Redis"
    description = "Provides dependencies for getting a Redis client"

    def _get_redis_options(self, override_conf: RedisConf | None):

        conf = override_conf or self.kitman.settings.plugins.redis

        return conf.get_redis_options()

    def _check(self, raise_exception: bool = True) -> bool:
        valid = super()._check(raise_exception)

        if not self.kitman.settings.plugins.redis:

            if raise_exception:
                self.fail("Config for redis plugin is not defined")
            else:
                return False

        return valid

    # Dependencies
    def get_client(self, override_conf: RedisConf | None = None) -> Redis:

        options = self._get_redis_options(override_conf)

        return Redis(**options)
