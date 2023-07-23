from typing import TYPE_CHECKING, ForwardRef, Generic, Type, TypeVar
from fastapi import FastAPI
from pydantic import BaseModel
from .services import BaseService

if TYPE_CHECKING:
    from kitman.conf import Settings

TModelsConfig = TypeVar("TModelsConfig", bound="BaseModel")
TServicesConfig = TypeVar("TServicesConfig", bound="BaseModel")
TDependenciesConfig = TypeVar("TDependenciesConfig", bound="BaseModel")


class BaseConfig:
    arbitrary_types_allowed = True


class ModelConfig(BaseModel):
    # TODO[pydantic]: The `Config` class inherits from another class, please create the `model_config` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    class Config(BaseConfig):
        pass

    ref: ForwardRef
    model: Type


class ServiceConfig(BaseModel):
    # TODO[pydantic]: The `Config` class inherits from another class, please create the `model_config` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    class Config(BaseConfig):
        pass


class DependencyConfig(BaseModel):
    # TODO[pydantic]: The `Config` class inherits from another class, please create the `model_config` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    class Config(BaseConfig):
        pass


class SimpleConfig(BaseModel):
    # TODO[pydantic]: The `Config` class inherits from another class, please create the `model_config` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    class Config(BaseConfig):
        pass


class AppConfig(
    BaseModel, Generic[TModelsConfig, TServicesConfig, TDependenciesConfig]
):
    # TODO[pydantic]: The `Config` class inherits from another class, please create the `model_config` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    class Config(BaseConfig):
        pass

    name: str
    namespace: str | None = None
    models: TModelsConfig | None = None
    services: TServicesConfig | None = None
    dependencies: TDependenciesConfig | None = None

    def install(app: FastAPI, settings: "Settings") -> FastAPI:
        return app
