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
from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel
import datetime
from uuid import uuid4

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


# Entities
class Entity(BaseModel):

    uid: UUID = Field(default_factory=uuid4)


class TimestampedEntity(Entity):
    created: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    @validator("updated", always=True)
    def set_updated(cls, value: datetime.datetime | None, **kwargs):

        return datetime.datetime.utcnow()


# Schemas
class Schema(BaseModel):
    class Config:
        orm_mode = True


# Pages
TPageItem = TypeVar("TPageItem", bound=Schema)


class Page(GenericModel, Generic[TPageItem]):

    page: int = 1
    size: int = 100
    total: int
    items: list[TPageItem]
    prev_page: int | None = None
    next_page: int | None = None
