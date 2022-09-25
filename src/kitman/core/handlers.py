from typing import TYPE_CHECKING, Any, TypeVar, Generic
from pydantic import BaseModel, validate_arguments
from fastapi import status
from fastapi.exceptions import HTTPException

if TYPE_CHECKING:
    from kitman import Kitman


TMessage = TypeVar("TMessage", bound=BaseModel)


class BaseHandler(Generic[TMessage]):

    kitman: "Kitman"
    handles: set[type[TMessage]] = set()

    def __new__(cls):

        klass = super().__new__(cls)

        klass.handle = validate_arguments(klass.handle)

        return klass

    async def handle(self, message: TMessage) -> bool:
        ...

    def fail(
        self,
        message: str,
        detail: str | dict | list[str | dict] | None = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        headers: dict[str, Any] | None = None,
    ):

        body = {"message": message}

        if detail:

            body["detail"] = detail

        raise HTTPException(status_code=status_code, detail=body, headers=headers)
