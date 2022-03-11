import datetime
from pydantic import BaseModel

class Schema(BaseModel):

    def __new__(cls, *args, **kwargs):

        klass = super().__new__(cls)

        orm_mode = getattr(klass.Config, "orm_mode", None)

        if not orm_mode:
            setattr(klass.Config, "orm_mode", True)

        return klass

class TimestampedSchema(Schema):
    created: datetime.datetime
    updated: datetime.datetime