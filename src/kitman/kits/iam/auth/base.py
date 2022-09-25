from collections.abc import Coroutine
import enum
from typing import Generic, Literal, TypeVar
from fastapi import Depends, Header, Query, Request
from pydantic import BaseModel
from pydantic.generics import GenericModel
from kitman import Plugin, Kitman, InstallableManager, TInstallableConf, TInstallable
from kitman.core import exceptions
from fastapi import status

from .. import domain

from kitman.core.domain import Location

# Location strategies
class BaseLocationStrategy:

    key: str
    location: Location

    def __init__(self, key: str):

        self.key = key

    def get_value(self, request: Request) -> str | int:

        raise NotImplementedError("Please implement get_value")


class HeaderLocationStrategy(BaseLocationStrategy):

    location = Location.header

    def get_value(self, request: Request) -> str | int:
        return request.headers.get(self.key)


class QueryLocationStrategy(BaseLocationStrategy):

    location = Location.query

    def get_value(self, request: Request) -> str | int:
        return request.query_params.get(self.key)


class CookieLocationStrategy(BaseLocationStrategy):

    location = Location.cookie

    def get_value(self, request: Request) -> str | int:
        return request.cookies.get(self.key)


# End location strategies


class BaseAuthenticationConf(GenericModel, Generic[domain.TUser]):

    get_user: Coroutine[list[str | int, bool, bool], None, domain.TUser | None]
    location: BaseLocationStrategy = HeaderLocationStrategy(key="Authentication")


TAuthenticationConf = TypeVar("TAuthenticationConf", bound=BaseAuthenticationConf)


class BaseAuthenticationPlugin(Plugin, Generic[TAuthenticationConf, domain.TUser]):

    conf: BaseAuthenticationConf | TAuthenticationConf

    def get_user_id(self, request: Request) -> str | int:

        return self.conf.location.get_value(request)

    async def current_user(
        self, active: bool = True, verified: bool = True, **kwargs
    ) -> Coroutine[None, None, domain.TUser]:
        async def get_current_user(
            active=active,
            verified=verified,
            user_id: str | int = Depends(self.get_user_id),
        ) -> domain.TUser:

            user = await self.conf.get_user(user_id, active, verified)

            if not user:
                raise exceptions.HTTPError(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return user

        return get_current_user
