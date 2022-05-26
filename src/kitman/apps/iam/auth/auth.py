from inspect import Parameter, Signature
from typing import Callable, Generic, Sequence, cast

from fastapi import Depends, Response, status
from makefun import with_signature

from kitman.core.domain import DependencyCallable
from .. import domain, errors
import re

from kitman.errors import HTTPError

INVALID_CHARS_PATTERN = re.compile(r"[^0-9a-zA-Z_]")
INVALID_LEADING_CHARS_PATTERN = re.compile(r"^[^a-zA-Z_]+")


def name_to_variable_name(name: str) -> str:
    """Transform a backend name string into a string safe to use as variable name."""
    name = re.sub(INVALID_CHARS_PATTERN, "", name)
    name = re.sub(INVALID_LEADING_CHARS_PATTERN, "", name)
    return name


def name_to_strategy_variable_name(name: str) -> str:
    """Transform a backend name string into a strategy variable name."""
    return f"strategy_{name_to_variable_name(name)}"


class AuthenticationBackend(Generic[domain.TUser]):

    name: str
    transport: domain.ITransport
    get_strategy: DependencyCallable[domain.IStrategy[domain.TSubjectId, domain.TUser]]

    def __init__(
        self,
        name: str,
        transport: domain.ITransport,
        get_strategy: DependencyCallable[
            domain.IStrategy[domain.TSubjectId, domain.TUser]
        ],
    ):

        self.name = name
        self.transport = transport
        self.get_strategy = get_strategy

    async def login(
        self, strategy: domain.IStrategy, user: domain.TUser, response: Response
    ):

        token = await strategy.write_token(user)
        return await self.transport.get_login_response(token, response)

    async def logout(
        self,
        strategy: domain.IStrategy,
        user: domain.TUser,
        token: str,
        response: Response,
    ):
        try:
            await strategy.destroy_token(token, user)
        except errors.StrategyDestroyNotSupportedError:
            pass

        try:
            await self.transport.get_logout_response(response)
        except errors.TransportLogoutNotSupportedError:
            return None


EnabledBackendsDependency = DependencyCallable[Sequence[AuthenticationBackend]]


class Authenticator:

    backends: list[AuthenticationBackend]
    get_user_service: domain.UserServiceDependency[domain.TSubjectId, domain.TUser]

    def __init__(
        self,
        backends: list[AuthenticationBackend],
        get_user_service: domain.UserServiceDependency[domain.TSubjectId, domain.TUser],
    ):

        self.backends = backends
        self.get_user_service = get_user_service

    def get_current_user_token(
        self,
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
        get_enabled_backends: EnabledBackendsDependency | None = None,
    ):

        signature = self._get_dependency_signature(get_enabled_backends)

        @with_signature(signature)
        async def current_user_token_dependency(*args, **kwargs):
            return await self._authenticate(
                *args,
                optional=optional,
                active=active,
                verified=verified,
                superuser=superuser,
                **kwargs,
            )

        return current_user_token_dependency

    def current_user(
        self,
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
        get_enabled_backends: EnabledBackendsDependency | None = None,
    ):
        signature = self._get_dependency_signature(get_enabled_backends)

        @with_signature(signature)
        async def current_user_dependency(*args, **kwargs):
            user, _ = await self._authenticate(
                *args,
                optional=optional,
                active=active,
                verified=verified,
                superuser=superuser,
                **kwargs,
            )
            return user

        return current_user_dependency

    async def _authenticate(
        self,
        *args,
        user_service: domain.IUserService[domain.TSubjectId, domain.TUser],
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
        **kwargs,
    ) -> tuple[domain.TUser | None, str | None]:
        user: domain.TUser | None = None
        token: str | None = None
        enabled_backends: Sequence[AuthenticationBackend] = kwargs.get(
            "enabled_backends", self.backends
        )
        for backend in self.backends:
            if backend in enabled_backends:
                token = kwargs[name_to_variable_name(backend.name)]
                strategy: domain.IStrategy[domain.TSubjectId, domain.TUser] = kwargs[
                    name_to_strategy_variable_name(backend.name)
                ]
                if token is not None:
                    user = await strategy.read_token(token, user_service)
                    if user:
                        break

        status_code = status.HTTP_401_UNAUTHORIZED
        if user:
            status_code = status.HTTP_403_FORBIDDEN
            if active and not user.is_active:
                status_code = status.HTTP_401_UNAUTHORIZED
                user = None
            elif (
                verified and not user.is_verified or superuser and not user.is_superuser
            ):
                user = None
        if not user and not optional:
            raise HTTPError(status_code=status_code)
        return user, token

    def _get_dependency_signature(
        self, get_enabled_backends: EnabledBackendsDependency | None = None
    ) -> Signature:
        try:
            parameters: list[Parameter] = [
                Parameter(
                    name="user_manager",
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    default=Depends(self.get_user_service),
                )
            ]

            for backend in self.backends:
                parameters += [
                    Parameter(
                        name=name_to_variable_name(backend.name),
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        default=Depends(cast(Callable, backend.transport.scheme)),
                    ),
                    Parameter(
                        name=name_to_strategy_variable_name(backend.name),
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        default=Depends(backend.get_strategy),
                    ),
                ]

            if get_enabled_backends is not None:
                parameters += [
                    Parameter(
                        name="enabled_backends",
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        default=Depends(get_enabled_backends),
                    )
                ]
            return Signature(parameters)
        except ValueError:
            raise errors.DuplicateBackendNamesError()
