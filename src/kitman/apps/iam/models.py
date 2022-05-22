from pydantic import EmailStr
from kitman.db.models import BaseModel, BaseMeta, ormar


class BaseUser(BaseModel):
    class Meta(BaseMeta):
        abstract = True

    username: str = ormar.String(max_length=255, unique=True)
    email: EmailStr = ormar.String()


class BaseCustomer(BaseModel):
    class Meta(BaseMeta):
        abstract = True

    name: str = ormar.String(max_length=255)
