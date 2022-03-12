import datetime
import uuid
import ormar

from saas_toolkit.config import SETTINGS


class BaseModel(ormar.Model):
    class Meta(SETTINGS.models.metadata):
        abstract = True

    id: uuid.UUID = ormar.UUID(
        uuid_format="string",
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        unique=True,
    )

    # created = fields.DatetimeField(auto_now_add=True)
    # updated = fields.DatetimeField(auto_now=True)
    created: datetime.datetime = ormar.DateTime(timezone=True)
    updated: datetime.datetime = ormar.DateTime(timezone=True, nullable=True)

    def __str__(self) -> str:

        return f"{self.__class__.__name__} with ID: {self.id}"

    async def save(self):

        if not self.created:
            self.created = datetime.datetime.now()

        return await super().save()

    async def update(self, **kwargs):

        self.updated = datetime.datetime.now()

        return await super().update(**kwargs)
