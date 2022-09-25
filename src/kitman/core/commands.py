import datetime
from typing import TYPE_CHECKING, TypeVar
from uuid import uuid4
from pydantic import BaseModel, Field, UUID4
from .events import DomainEvent
from .handlers import BaseHandler

if TYPE_CHECKING:
    from kitman import Kitman


class Command(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)
    created: datetime.datetime = Field(default_factory=datetime.datetime.now)


class CommandHandler(BaseHandler[Command]):
    async def emit(self, event: DomainEvent):

        await self.kitman.emit(event)


TCommandHandler = TypeVar("TCommandHandler", bound=CommandHandler)
