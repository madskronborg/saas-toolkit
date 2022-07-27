from typing import Generic

from pydantic import BaseModel

from kitman.kits.iam import domain

from .base import BaseAuthenticationConf, BaseAuthenticationPlugin


class TokenAuthenticationConf(BaseAuthenticationConf, Generic[domain.TUser]):

    token_model: type[BaseModel] | None = None
    token_data_model: type[BaseModel] | None = None
