from typing import Any

from typing_extensions import Self

from kitman import Kitman, Plugin
from kitman.core import dynamic
from kitman.kitman import InstallableManager
from kitman.plugins.ormar.models import BaseModel

from .client import Redis


class RedisPluginConf(BaseModel):

    __redis_options: list[str] = []

    def __new__(cls: type[Self]) -> Self:

        callable_types = dynamic.get_callable_types(Redis.__init__)

        for parameter in callable_types.parameters.values():

            name = f"REDIS_{parameter.name.upper()}"

            cls = dynamic.add_attr_to_class(
                cls, name, parameter.default, parameter.annotation
            )

            cls.__redis_options.append(name)

        return super().__new__(cls)

    def get_redis_options(self, **kwargs) -> dict[str, Any]:

        options = {
            option.replace("REDIS_", "").lower(): getattr(self, option)
            for option in self.__redis_options
        }

        return {**options, **kwargs}


class RedisPluginManager(InstallableManager["RedisPlugin", RedisPluginConf]):
    def check(self, raise_exception: bool = True) -> bool:
        valid = super().check(raise_exception)

        if not self.parent.settings:

            if raise_exception:
                self.fail("Config for redis plugin is not defined")
            else:
                return False

        return valid


class RedisPlugin(Plugin[RedisPluginConf]):
    name = "Redis"
    description = "Provides dependencies for getting a Redis client"
    manager = RedisPluginManager()

    def _get_redis_options(self, override_conf: RedisPluginConf | None):

        conf = override_conf or self.settings

        return conf.get_redis_options()

    # Dependencies
    def get_client(self, override_conf: RedisPluginConf | None = None) -> Redis:

        options = self._get_redis_options(override_conf)

        return Redis(**options)
