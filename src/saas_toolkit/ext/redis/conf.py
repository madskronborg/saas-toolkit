from typing import Any
from typing_extensions import Self
from pydantic import BaseSettings
from saas_toolkit.core import dynamic
from .client import Redis, Sentinel


class RedisSettings(BaseSettings):

    __redis_options: list[str] = []

    def __new__(cls: type[Self]) -> Self:

        parameters, return_type = dynamic.get_callable_types(Redis.__init__)

        for parameter in parameters:

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
