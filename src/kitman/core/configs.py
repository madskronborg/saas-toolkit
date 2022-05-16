from typing import Type
from pydantic import BaseModel
from .services import BaseService


class BaseConfig(BaseModel):
    class Config:
        arbitrary_types_allowed = True


class BaseModelConfig(BaseConfig):

    pass


class BaseServiceConfig(BaseConfig):

    pass


class BaseAppConfig(BaseConfig):

    name: str
    models: BaseModelConfig | None = None
    services: BaseServiceConfig | None = None
