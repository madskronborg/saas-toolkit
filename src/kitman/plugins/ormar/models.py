import datetime
from typing import TYPE_CHECKING
import uuid
import ormar
from ormar.models import T
from ormar.relations.querysetproxy import QuerysetProxy

from kitman import exceptions

# Queryset
class BaseQueryset(ormar.QuerySet[T]):
    async def get_or_404(self, *args, **kwargs) -> T:

        entity = await self.get_or_none(*args, **kwargs)

        if entity is None:
            raise exceptions.NotFound(f"{self.model.__class__.__name__} not found")

        return entity


# Models
class BaseModel(ormar.Model):
    class Meta:
        abstract = True

    if TYPE_CHECKING:
        objects: BaseQueryset["BaseModel"]

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
