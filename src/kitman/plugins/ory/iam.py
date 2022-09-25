from typing import Generic
from uuid import UUID
from fastapi import Request
from fastapi.security.base import SecurityBase
from kitman.kits.iam.auth.auth import AuthenticationBackend

from kitman.kits.iam.exceptions import StrategyDestroyNotSupportedError
from . import schemas
from fastapi import status
from kitman.kits.iam.auth import NoOpTransport
from kitman.kits.iam.domain import (
    IStrategy,
    IUser,
    IUserService,
    TSubjectId,
    TUser,
    ITransport,
)
from kitman import exceptions
from kitman.conf import settings

UserService = settings.kits.iam.services.users


class UserIDHeader(SecurityBase):
    def __init__(
        self,
        *,
        name: str,
        scheme_name: str | None = None,
        description: str | None = None,
        auto_error: bool = True,
    ):
        self.model: schemas.UserId = schemas.UserId(
            **{"in": "header"}, name=name, description=description
        )
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(self, request: Request) -> str | None:
        user_id: str = request.headers.get(self.model.name)
        if not user_id:
            if self.auto_error:
                raise exceptions.HTTPError(
                    status_code=status.HTTP_403_FORBIDDEN,
                    message=f"Not authenticated. Header {self.model.name} did not contain a user id.",
                )
            else:
                return None
        return user_id


class OryUserIdTransport(NoOpTransport):
    scheme: UserIDHeader

    def __init__(self, name: str = "X-USER-ID", description: str | None = None):
        self.scheme = UserIDHeader(name=name, description=description, auto_error=False)


class OryUserIdStrategy(IStrategy, Generic[TSubjectId, TUser]):
    async def read_token(
        self, token: str | None, service: IUserService[TSubjectId, TUser]
    ) -> TUser | None:

        return token

    async def write_token(self, user: TUser) -> UUID:
        return user.id

    async def destroy_token(self, token: str, user: TUser) -> None:
        raise StrategyDestroyNotSupportedError(
            "A Ory User ID has to be invalidated through Ory Kratos."
        )
