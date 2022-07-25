from typing import Generic, Protocol, TypeVar

from uuid import UUID

from fastapi.security.base import SecurityBase
from fastapi import Response

from kitman.core.domain import DependencyCallable, OpenAPIResponseType, IModel
from kitman.core.schemas import Schema

# Types
TUser = TypeVar("TUser", bound="IUser")
TSubject = TypeVar("TSubject")
TSubjectId = TypeVar("TSubjectId", bound=str | UUID | dict)
TCheckResponse = TypeVar("TCheckResponse")
TGrantResponse = TypeVar("TGrantResponse")
TRevokeResponse = TypeVar("TRevokeResponse")
TInspectResponse = TypeVar("TInspectResponse")
TLoginResponse = TypeVar("TLoginResponse", bound=Schema)
TLogoutResponse = TypeVar("TLogoutResponse", bound=Schema)

# Value objects
Obj = str | UUID
Relation = str
Namespace = str | None

# Models
class IUser(IModel):

    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    is_superuser: bool


# Services


class IUserService(
    Protocol,
    Generic[
        TSubjectId,
        TUser,
    ],
):
    async def get_by_id(self, subject_id: TSubjectId) -> TUser:
        ...


UserServiceDependency = DependencyCallable[IUserService[TSubjectId, TUser]]

# Strategies
class IStrategy(Protocol, Generic[TSubjectId, TUser]):
    async def read_token(
        self, token: str | None, service: IUserService[TSubjectId, TUser]
    ) -> TUser | None:
        ...

    async def write_token(self, user: TUser) -> str:
        ...

    async def destroy_token(self, token: str, user: TUser) -> None:
        ...


# Transports
class ITransport(Protocol, Generic[TLoginResponse, TLogoutResponse]):

    scheme: SecurityBase

    async def get_login_response(
        self, token: str, response: Response
    ) -> TLoginResponse:
        ...

    async def get_logout_response(
        self, token: str, response: Response
    ) -> TLogoutResponse:
        ...

    @staticmethod
    def get_openapi_login_responses_sucess() -> OpenAPIResponseType:
        ...

    @staticmethod
    def get_openapi_logout_responses_success() -> OpenAPIResponseType:
        ...
