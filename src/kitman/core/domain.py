import datetime
import enum
from collections import OrderedDict
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Coroutine,
    Generator,
    Generic,
    Protocol,
    Self,
    TypeVar,
)
from uuid import UUID, uuid4

import pycountry
from phonenumbers import (
    NumberParseException,
    PhoneNumberFormat,
    PhoneNumberType,
    format_number,
    is_valid_number,
    number_type,
)
from phonenumbers import parse as parse_phone_number
from pydantic import ConfigDict, BaseModel, Field, constr, create_model, root_validator, validator
from pydantic.fields import FieldInfo, ModelField

# Value objects
OpenAPIResponseType = dict[int | str, dict[str, Any]]

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


# Schemas
class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SchemaOut(Schema):
    id: UUID


# Entities
class Entity(BaseModel):

    uid: UUID = Field(default_factory=uuid4)

    @classmethod
    def to_schema(
        cls,
        name: str,
        fields: list[str | tuple[str, ModelField]],
        validators: dict[str, callable] = None,
        partial: bool = False,
        __base__: type["Schema"] = Schema,
    ):

        new_fields: OrderedDict[str, ModelField] = OrderedDict()
        new_annotations: OrderedDict[str, type | None] = OrderedDict()

        for field in fields:
            field_name: str
            field_config: ModelField

            if isinstance(field, str):
                field_name = field
                field_config = cls.__fields__.get(field, None)

                if not field_config:
                    raise ValueError(
                        f"Field with name: {field} does not exist on model: {cls.__name__}"
                    )

            if isinstance(field, tuple):
                field_name, field_config = field
                field_config.set_config(cls.Config)

            if partial:
                field_config.required = False
                field_config.annotation = field_config.annotation | None

            new_fields.update({field_name: field_config})
            new_annotations.update({field_name: field_config.annotation})

        model = create_model(
            name,
            __base__=__base__,
            __validators__=validators,
        )

        model.__fields__.update(new_fields)
        model.__annotations__.update(new_annotations)

        return model


class TimestampedEntity(Entity):
    created: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("updated", always=True)
    def set_updated(cls, value: datetime.datetime | None, **kwargs):

        return datetime.datetime.utcnow()


# Pages
TPageItem = TypeVar("TPageItem", bound=Schema)


class Page(BaseModel, Generic[TPageItem]):

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
