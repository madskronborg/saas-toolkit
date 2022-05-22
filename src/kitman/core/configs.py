from typing import ForwardRef, Generic, Type, TypeVar
from pydantic import BaseModel
from .services import BaseService
from pydantic.generics import GenericModel

TModelsConfig = TypeVar("TModelsConfig")
TServicesConfig = TypeVar("TServicesConfig")


class BaseConfig:
    arbitrary_types_allowed = True


class ModelConfig(BaseModel):
    class Config(BaseConfig):
        pass

    ref: ForwardRef
    model: Type


class ServiceConfig(BaseModel):
    class Config(BaseConfig):
        pass


class SimpleConfig(BaseModel):
    class Config(BaseConfig):
        pass


class AppConfig(GenericModel, Generic[TModelsConfig, TServicesConfig]):
    class Config(BaseConfig):
        pass

    name: str
    models: TModelsConfig | None = None
    services: TServicesConfig | None = None
