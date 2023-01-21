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
from pydantic import BaseModel, Field, validator, constr
from pydantic.generics import GenericModel
import datetime
from uuid import uuid4
import pycountry
from phonenumbers import (
    NumberParseException,
    PhoneNumberFormat,
    PhoneNumberType,
    format_number,
    is_valid_number,
    number_type,
    parse as parse_phone_number,
)


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


# Country
def get_countries() -> pycountry.ExistingCountries:

    return pycountry.countries


class Country(constr(max_length=2, strip_whitespace=True)):
    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        # __modify_schema__ should mutate the dict it receives in place,
        # the returned value will be ignored
        field_schema.update(
            # simplified regex here for brevity, see the wikipedia link above
            # some example postcodes
            examples=["DK"],
        )

    @classmethod
    def validate(cls, v):
        if v is None:
            return v

        country: object | None = pycountry.countries.get(alpha_2=v)

        if not country:
            raise ValueError("Please provide a valid country")

        return country.alpha_2


# Address
class Address(BaseModel):

    street: str
    city: str
    state: str
    zip: str
    country: Country


# PhoneNumber
MOBILE_NUMBER_TYPES = PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE_OR_MOBILE


class PhoneNumber(constr(max_length=50, strip_whitespace=True)):
    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema: dict):
        # __modify_schema__ should mutate the dict it receives in place,
        # the returned value will be ignored
        field_schema.update(
            # simplified regex here for brevity, see the wikipedia link above
            # some example postcodes
            examples=["+4512345678"],
        )

    @classmethod
    def validate(cls, v):
        if v is None:
            return v

        try:
            n = parse_phone_number(v, "DK")
        except NumberParseException as e:
            raise ValueError("Please provide a valid mobile phone number") from e

        if not is_valid_number(n) or number_type(n) not in MOBILE_NUMBER_TYPES:
            raise ValueError("Please provide a valid mobile phone number")

        return format_number(
            n,
            PhoneNumberFormat.INTERNATIONAL,
        )

    def __repr__(self):
        return f"PhoneNumber({super().__repr__()})"
