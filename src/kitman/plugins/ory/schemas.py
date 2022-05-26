from pydantic import Field
from fastapi.openapi.models import SecurityBase


class UserId(SecurityBase):

    type_: str = Field("header", alias="type")
    in_: str = Field("header", alias="in")
    name: str
