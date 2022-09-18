import datetime
from typing import TYPE_CHECKING, TypeVar
from uuid import uuid4
from pydantic import BaseModel, Field, UUID4
from .events import DomainEvent
from multimethod import multimeta

if TYPE_CHECKING:
    from kitman import Kitman


class Command(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)
    created: datetime.datetime = Field(default_factory=datetime.datetime.now)


class CommandHandler(metaclass=multimeta):

    kitman: "Kitman"
    handles: list[type[Command]] = []

    async def handle(self, message: Command) -> bool:
        ...

    async def emit(self, event: DomainEvent):

        await self.kitman.emit(event)


TCommandHandler = TypeVar("TCommandHandler", bound=CommandHandler)
