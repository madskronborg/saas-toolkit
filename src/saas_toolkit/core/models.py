import datetime
import uuid
import ormar

from saas_toolkit.conf import SETTINGS


class BaseMeta(ormar.ModelMeta):
    metadata = SETTINGS.sql.metadata
    database = SETTINGS.sql.database


class BaseModel(ormar.Model):
    class Meta:
        abstract = True
        metadata = SETTINGS.sql.metadata
        database = SETTINGS.sql.database

    id: uuid.UUID = ormar.UUID(
        uuid_format="string",
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        unique=True,
    )

    created: datetime.datetime = ormar.DateTime(timezone=True, nullable=True)
    updated: datetime.datetime = ormar.DateTime(timezone=True, nullable=True)

    def __str__(self) -> str:

        return f"{self.__class__.__name__} with ID: {self.id}"

    async def save(self):

        now = datetime.datetime.now()

        if not self.created:
            self.created = now

        self.updated = now

        return await super().save()

    async def update(self, **kwargs):

        self.updated = datetime.datetime.now()

        return await super().update(**kwargs)


class OrderableMixin:
    class MetaOptions:

        orders_by = ["order"]

    order: int = ormar.SmallInteger(default=1)
