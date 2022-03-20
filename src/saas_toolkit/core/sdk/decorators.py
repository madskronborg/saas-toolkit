from functools import wraps

from typing import Optional, Type, TypeVar
from .request import Request
from .response import Response
from httpx import Response as HTTPXResponse
from pydantic import parse_obj_as

TRequest = TypeVar("TRequest", bound=Request)
TResponse = TypeVar("TResponse", bound=Response)


def get_request_data(
    data: Optional[Type[[TRequest]]] = None,
    request: Optional[dict | list | TRequest] = None,
) -> Optional[TRequest | list[TRequest]]:

    if not request:
        return None

    if not data:
        return None

    if isinstance(request, Request):
        return request

    if isinstance(request, dict):
        return data(**request)

    if isinstance(request, list):
        return parse_obj_as(list[data], request)

    # Error handling


def get_response_data(
    http_response: HTTPXResponse,
    responses: Optional[Type[TResponse] | dict[int, Type[TResponse]]] = None,
) -> dict | TResponse:

    data: Optional[dict | str] = None

    try:
        data = http_response.json()
    except:
        data = http_response.text()

    if not isinstance(data, (dict, list)):
        return data

    if not responses:
        return data

    if issubclass(responses, Response):

        if isinstance(data, dict):
            return responses(**data)

        if isinstance(data, list):
            return parse_obj_as(list[responses], data)

    if issubclass(responses, dict):

        status_code = http_response.status_code

        # If status_code is a key in response_model, use key's value as response model
        if response_model_class := getattr(responses, status_code, None):
            if isinstance(data, dict):
                return response_model_class(**data)

            if isinstance(data, list):
                return parse_obj_as(list[response_model_class], data)

        return data

    raise TypeError(
        "responses has to be None, a subclass of Response or a dictionary of HTTP Status Codes and Response subclasses"
    )


def action(
    data: Optional[Type[[TRequest]]] = None,
    responses: Optional[Type[TResponse] | dict[int, Type[TResponse]]] = None,
    debug: bool = False,
):
    def decorator(func):
        async def wrapper(*args, **kwargs):

            result = await func(*args, **kwargs)

        return wrapper

    return decorator
