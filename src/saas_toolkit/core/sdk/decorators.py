from functools import wraps
import inspect

from typing import Optional, Type, TypeVar, cast, get_args, get_origin
from .request import Request, Params
from .response import Response
import httpx
from pydantic import ValidationError, parse_obj_as, validate_arguments
from saas_toolkit import logger
from . import errors

TRequest = TypeVar("TRequest", bound=Request)
TResponse = TypeVar("TResponse", bound=Response)
TParams = TypeVar("TParams", bound=Params)


def get_params(
    sig: inspect.Signature, params: Optional[dict | TParams] = None
) -> Optional[TParams]:

    params_type = sig.parameters["params"].annotation

    if isinstance(params, params_type):
        return params

    return parse_obj_as(params_type, params)


def get_request_data(
    sig: inspect.Signature,
    data: Optional[dict | list | TRequest] = None,
) -> Optional[TRequest | list[TRequest]]:

    if not data:
        return None

    data_type = sig.parameters["data"].annotation

    if isinstance(data, data_type):
        return data

    return parse_obj_as(data_type, data)


def get_response_data(
    sig: inspect.Signature,
    http_response: httpx.Response,
    response: Optional[Type[Response]] = None,
    responses: Optional[dict[int, Type[TResponse]]] = None,
    raw: bool = False,
) -> dict | list | TResponse:

    if raw:
        return http_response

    response_type = sig.return_annotation

    data: Optional[dict | str] = None

    try:
        data = http_response.json()
    except:
        data = http_response.text()

    if not isinstance(data, (dict, list)):
        return data

    if not (responses or response_type):
        return data

    if response:

        return parse_obj_as(response, data)

    if responses:

        status_code = http_response.status_code

        # If status_code is a key in response_model, use key's value as response model
        if response_model_class := responses.get(status_code, None):
            return parse_obj_as(response_model_class, data)

        return data

    if response_type:

        return parse_obj_as(response_type, data)

    raise TypeError(
        "responses has to be None, a subclass of Response or a dictionary of HTTP Status Codes and Response subclasses"
    )


def action(
    response: Optional[Type[Response]] = None,
    responses: Optional[dict[int, Type[TResponse]]] = None,
    debug: bool = False,
):
    def decorator(func):

        sig = inspect.signature(func)

        is_debug_mode = debug

        func = validate_arguments(func)

        @wraps(func)
        async def wrapper(*args, **kwargs):

            debug = kwargs.pop("debug", is_debug_mode)
            raw = kwargs.pop("raw", False)
            print("Debug is:", debug, "Raw is:", raw)

            ba = sig.bind(*args, **kwargs)

            data = ba.arguments.get("data", None)

            if data:
                data = get_request_data(sig, data)
                ba.arguments["data"] = data

            params = ba.arguments.get("params", None)

            if params:
                params = get_params(sig, params)
                ba.arguments["params"] = params

            ba.apply_defaults()

            print("Arguments are:", ba.arguments)

            # Validate function arguments before starting request
            func.validate(*ba.args, **ba.kwargs)

            http_response = None

            try:
                http_response: httpx.Response = await func(*ba.args, **ba.kwargs)
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

            http_response = get_response_data(
                sig, http_response, response, responses, raw=raw
            )

            return http_response

        # TODO: Update function signature to show debug: bool = False _and_ raw: bool = False in intellisense / python
        """ parameters = (
            *sig.parameters.values(),
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
        )

        sig = sig.replace(parameters=parameters)
        func.__signature__ = sig  """
        func.__annotations__["debug"] = bool
        func.__annotations__["raw"] = bool

        return wrapper

    return decorator
