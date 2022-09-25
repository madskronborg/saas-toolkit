from makefun import wraps
import inspect

from typing import Callable, Optional, Type, TypeVar, TypedDict
from .request import Request, QueryParams
from .response import Response
import httpx
from pydantic import parse_obj_as, validate_arguments
from kitman import logger
from kitman.core import dynamic
from . import exceptions
from dataclasses import dataclass

TRequest = TypeVar("TRequest", bound=Request)
TResponse = TypeVar("TResponse", bound=Response)
TParams = TypeVar("TParams", bound=QueryParams)


@dataclass
class SDKActionConfig(dynamic.ActionConfig):
    response: Optional[Type[Response]]
    responses: Optional[dict[int, Type[TResponse]]]
    debug: bool


def handle_response(
    http_response: httpx.Response,
    callable_types: dynamic.CallableTypes,
    config: SDKActionConfig,
    *args,
    **kwargs,
) -> httpx.Response:

    debug = config.debug or kwargs.get("debug")

    try:
        http_response.raise_for_status()

    except httpx.HTTPStatusError as exc:

        if exc.request.method in ["GET", "DELETE"]:
            if debug:
                logger.error(
                    f"Error response {exc.response.status_code} while requesting {exc.request.url!r}."
                )

        else:

            if debug:
                logger.error(
                    f"Error response {exc.response.status_code} while requesting {exc.request.url!r}. \n\n Body is:\n{data}\n\nHeaders are:\n{exc.request.headers}"
                )

        raise

    return http_response


def get_response_data(
    http_response: httpx.Response,
    callable_types: dynamic.CallableTypes,
    config: SDKActionConfig,
    *args,
    **kwargs,
) -> dict | list | TResponse:

    raw = kwargs.get("raw")

    if raw:
        return http_response

    response_type = callable_types.return_type

    data: Optional[dict | str] = None

    try:
        data = http_response.json()
    except:
        data = http_response.text()

    if not isinstance(data, (dict, list)):
        return data

    if not (config.responses or response_type):
        return data

    if config.response:

        return parse_obj_as(config.response, data)

    if config.responses:

        status_code = http_response.status_code

        # If status_code is a key in response_model, use key's value as response model
        if response_model_class := config.responses.get(status_code, None):
            return parse_obj_as(response_model_class, data)

        return data

    if response_type:

        return parse_obj_as(response_type, data)

    raise TypeError(
        "responses has to be None, a subclass of Response or a dictionary of HTTP Status Codes and Response subclasses"
    )


# New action
def action(
    response: Optional[Type[Response]] = None,
    responses: Optional[dict[int, Type[TResponse]]] = None,
    debug: bool = False,
):
    def decorator(
        func: Callable[dynamic.TParams, dynamic.TReturnType]
    ) -> Callable[dynamic.TParams, dynamic.TReturnType]:

        return dynamic.make_action(
            func,
            config=SDKActionConfig(response, responses, debug),
            post_hooks=[handle_response, get_response_data],
            append_args=[
                inspect.Parameter(
                    "debug",
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    default=False,
                    annotation=bool,
                ),
                inspect.Parameter(
                    "raw",
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    default=False,
                    annotation=bool,
                ),
            ],
        )

    return decorator
