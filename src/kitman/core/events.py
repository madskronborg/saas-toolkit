from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from uuid import uuid4
from pydantic import BaseModel, Field, UUID4
import datetime
from asyncio import gather
from .handlers import BaseHandler

if TYPE_CHECKING:
    from kitman import Kitman


class DomainEvent(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)
    created: datetime.datetime = Field(default_factory=datetime.datetime.now)


class EventHandler(BaseHandler[DomainEvent]):

    handles: set[DomainEvent] = set()


# Emitters
class BaseEmitter(ABC):

    kitman: "Kitman"

    def bind(self, kitman: "Kitman"):
        self.kitman = kitman

    @abstractmethod
    async def emit(self, event: DomainEvent):
        pass


class ProcessEmitter(BaseEmitter):
    async def emit(self, event: DomainEvent):

        event_handlers = self.kitman.events.get(type(event), None)

        if not event_handlers:
            return

        if not event_handlers:
            return

        await gather([handler(event) for handler in event_handlers])
