from typing import TYPE_CHECKING, Any, Callable, TypeVar, Generic
from pydantic import BaseModel, validate_arguments
from fastapi import status
from fastapi.exceptions import HTTPException
from functools import wraps
from kitman.core import dynamic

if TYPE_CHECKING:
    from kitman import Kitman


TMessage = TypeVar("TMessage", bound=BaseModel)


def validate_handler(handler: type["BaseHandler"]):
    def decorator(
        func: Callable[dynamic.TParams, dynamic.TReturnType]
    ) -> Callable[dynamic.TParams, dynamic.TReturnType]:
        @wraps(func)
        async def wrapper(
            *args: dynamic.TParams.args, **kwargs: dynamic.TParams.kwargs
        ) -> dynamic.TReturnType:

            bound_params = dynamic.get_bound_params(
                dynamic.get_callable_types(func), *args, **kwargs
            )

            message: BaseModel = bound_params.arguments.get("message", None)

            if not type(message) in handler.handles:

                raise TypeError(
                    f"Type {type(message).__name__} is not handled by handler {handler.__name__}. Handler only handles: {handler.handles}"
                )

            result = await func(*args, **kwargs)

            return result

        return wrapper

    return decorator


class BaseHandler(Generic[TMessage]):

    kitman: "Kitman"
    handles: set[type[TMessage]] = set()

    def __new__(cls, *args, **kwargs):

        klass = super().__new__(cls)

        klass.handle = validate_handler(klass)(klass.handle)

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
