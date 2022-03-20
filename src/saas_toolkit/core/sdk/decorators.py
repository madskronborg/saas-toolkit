from functools import wraps
import inspect

from typing import Optional, Type, TypeVar, get_origin
from .request import Request, Params
from .response import Response
import httpx
from pydantic import parse_obj_as, validate_arguments
from saas_toolkit import logger
from . import errors

TRequest = TypeVar("TRequest", bound=Request)
TResponse = TypeVar("TResponse", bound=Response)
TParams = TypeVar("TParams", bound=Params)


def get_params(
    sig: inspect.Signature, params: Optional[dict | TParams] = None
) -> Optional[TParams]:

    if not params:
        return None

    params_type = sig.parameters["params"].annotation

    if isinstance(params, params_type):
        return params

    if isinstance(params, dict):

        if issubclass(params_type, Params):
            return Params(**params)
        if isinstance(params, dict):
            return params

    raise errors.InvalidParams(
        {
            "detail": f"Invalid params. Provided {type(params)} when expecting types dict or Params"
        }
    )


def get_request_data(
    sig: inspect.Signature,
    data: Optional[dict | list | TRequest] = None,
) -> Optional[TRequest | list[TRequest]]:

    if not data:
        return None

    data_type = sig.parameters["data"].annotation

    if isinstance(data, data_type):
        return data

    if isinstance(data, dict):

        if issubclass(data_type, Response):

            return data_type(**data)

        return data

    if isinstance(data, list):

        if issubclass(data_type, Response):
            return parse_obj_as(list[data], data)

        return data

    # Error handling
    raise errors.InvalidData(
        {
            "detail": f"Invalid data. Provided {type(data)} when expecting types dict, list or Request"
        }
    )


def get_response_data(
    sig: inspect.Signature,
    http_response: httpx.Response,
    responses: Optional[Type[TResponse] | dict[int, Type[TResponse]]] = None,
) -> dict | list | TResponse:

    response_type = sig.return_annotation
    response_type_origin = get_origin(response_type) or response_type
    print(
        "Response Type:", response_type, "response_type_origin:", response_type_origin
    )

    data: Optional[dict | str] = None

    try:
        data = http_response.json()
    except:
        data = http_response.text()

    if not isinstance(data, (dict, list)):
        return data

    if not (responses or response_type):
        return data

    if responses:

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

    if response_type:

        if issubclass(response_type_origin, Response):

            return response_type(**data)

        if issubclass(response_type_origin, dict):

            return data

        if issubclass(response_type_origin, list):
            return parse_obj_as(response_type, data)

    raise TypeError(
        "responses has to be None, a subclass of Response or a dictionary of HTTP Status Codes and Response subclasses"
    )


def action(
    responses: Optional[Type[TResponse] | dict[int, Type[TResponse]]] = None,
    debug: bool = False,
):
    def decorator(func):

        sig = inspect.signature(func)

        func = validate_arguments(func)

        is_debug_mode = debug

        @wraps(func)
        async def wrapper(*args, **kwargs):

            debug = kwargs.pop("debug", is_debug_mode)

            ba = sig.bind(*args, **kwargs)

            data = ba.arguments.get("data", None)

            if data:
                data = get_request_data(sig, data)
                sig.parameters["data"] = data

            params = ba.arguments.get("params", None)

            if params:
                params = get_params(sig, params)
                sig.parameters["params"] = params

            ba.apply_defaults()

            # Validate function arguments before starting request
            func.validate(*ba.args, **ba.kwargs)

            response = None

            try:
                response: httpx.Response = await func(*ba.args, **ba.kwargs)
                response.raise_for_status()

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

            response = get_response_data(sig, response, responses)

            return response

        return wrapper

    return decorator
