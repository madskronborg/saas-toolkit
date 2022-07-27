import enum
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Coroutine,
    Protocol,
    Generic,
    Generator,
)
from uuid import UUID

from ordered_set import TypeVar

# Value objects
OpenAPIResponseType = dict[int, str, dict[str, Any]]

RETURN_TYPE = TypeVar("RETURN_TYPE")

DependencyCallable = Callable[
    ...,
    RETURN_TYPE
    | Coroutine[None, None, RETURN_TYPE]
    | AsyncGenerator[RETURN_TYPE, None]
    | Generator[RETURN_TYPE, None, None],
]


class IModel(Protocol):
    id: UUID


class IService(Protocol):
    pass


class Location(str, enum.Enum):
    header = "header"
    query = "query"
    cookie = "cookie"
