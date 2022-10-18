from inspect import BoundArguments, signature, Signature, Parameter, iscoroutinefunction
from typing import (
    Any,
    Callable,
    Concatenate,
    Generic,
    ParamSpec,
    Type,
    TypeVar,
    Literal,
    cast,
)
from pydantic import parse_obj_as, validate_arguments
from makefun import wraps
from collections import OrderedDict
from dataclasses import dataclass
from collections.abc import Coroutine

from concurrent.futures import ThreadPoolExecutor
import asyncio
import string

TAnnotation = TypeVar("TAnnotation")
TType = TypeVar("TType", bound=Type)
TParams = ParamSpec("TParams")
TReturnType = TypeVar("TReturnType")
TActionConfig = TypeVar("TActionConfig", bound="ActionConfig")

# String


def get_placeholders_from_str(value: str) -> list[str]:

    placeholder_names = [
        name for text, name, spec, conv in string.Formatter().parse(value) if name
    ]

    return placeholder_names


# Callables


@dataclass
class CallableTypes(Generic[TReturnType]):

    parameters: OrderedDict[str, Parameter]
    return_type: TReturnType
    sig: Signature


class ActionConfig:
    pass


def make_async(func: Callable[TParams, TReturnType]) -> Callable[TParams, TReturnType]:
    """
    make_async

    Makes sure func is async. If it is not async, it will wrap it as a future and execute it in a ThreadPool.

    Args:
            func (Callable[TParams, TReturnType | Coroutine[None, None, TReturnType]]): A sync or async function

    Returns:
            Callable[TParams, Coroutine[None, None, TReturnType]]: An async function
    """

    pool = ThreadPoolExecutor()

    @wraps(func)
    async def wrapper(*args: TParams.args, **kwargs: TParams.kwargs) -> TReturnType:

        if iscoroutinefunction(func):
            return await func(*args, **kwargs)

        future = pool.submit(func, *args, **kwargs)

        return await asyncio.wrap_future(future)

    return wrapper


def get_callable_types(
    func: Callable[TParams, TReturnType], include_self: bool = True
) -> CallableTypes[TReturnType]:

    sig = signature(func, eval_str=True)

    parameters: OrderedDict[str, Parameter] = OrderedDict(**sig.parameters)

    if not include_self:
        if "self" in parameters:
            parameters.pop("self")

    return CallableTypes(
        parameters=parameters, return_type=sig.return_annotation, sig=sig
    )


def get_bound_params(callable_types: CallableTypes, *args, **kwargs) -> BoundArguments:

    bound_params = callable_types.sig.bind(*args, **kwargs)

    for param_name, param_value in bound_params.arguments.items():

        bound_params.arguments[param_name] = convert_value_to_type(
            param_value, callable_types.parameters[param_name].annotation
        )

    bound_params.apply_defaults()

    return bound_params


def convert_value_to_type(value: Any, annotation: TAnnotation) -> TAnnotation:
    """
    convert_value_to_type

    Convert a value to the specified type or raise an error

    Args:
            annotation (TAnnotation): The desired type to convert the value to
            value (Any): Any value

    Returns:
            TAnnotation: The value in the desired type
    """

    if annotation == Signature.empty:
        return value

    return parse_obj_as(annotation, value)


def make_action(
    func: Callable[TParams, TReturnType],
    config: TActionConfig | None = None,
    pre_hooks: list[
        Callable[
            Concatenate[BoundArguments, CallableTypes, TActionConfig | None, TParams],
            BoundArguments,
        ]
    ] = [],
    post_hooks: list[
        Callable[
            Concatenate[TReturnType, CallableTypes, TActionConfig | None, TParams],
            TReturnType,
        ]
    ] = [],
    # Makefun wraps settings
    append_args: list[Parameter] = [],
) -> Callable[TParams, TReturnType]:
    """
    make_action

    Decorator factory for creating actions.

    Actions are characterized by:

    - Arguments are type validated
    - Result will always be a coroutine
    - Supports pre_hooks to manipulate arguments and keyword arguments before calling the wrapped function
    - Supports post_hooks to alter the result of calling the wrapped function

    IMPORTANT

    `pre_hooks` and `post_hooks` are called in order, therefore, any alterations you make in a previous hook will be present in the following hooks.

    Example:
            def log_args(params: BoundArguments, callable_types: CallableTypes, config: TActionConfig | None, *args, **kwargs) -> BoundArguments:

                            print("Params are:", str(params))

                            return params

            async def log_result_to_server(result: TReturnType, callable_types: CallableTypes, config: TActionConfig | None, *args, **kwargs):

                    # Make async request to server ...

                    return result

            def action(func: Callable[TParams, TReturnType]):

               return make_action(func, pre_hooks=[log_args], post_hooks=[log_result_to_server])


    Args:
            func (Callable[TParams, TReturnType]): A function the decorator will wrap
            config (TActionConfig, optional): A config that will be passed to hooks. Default is None.
            pre_hooks (list[ Callable[ [BoundArguments, CallableTypes, TActionConfig | None, TParams], BoundArguments  |  Coroutine[None, None, BoundArguments], ] ], optional): A list of functions that can alter arguments and keyword arguments that will be passed to the wrapped function. Defaults to [].
            post_hooks (list[ Callable[ [TReturnType, CallableTypes, TActionConfig | None, TParams], TReturnType  |  Coroutine[None, None, TReturnType], ] ], optional): A list of functions that can alter the result of calling the wrapped function. Defaults to [].

            **Makefun**
            append_args (list[Parameter]): A list of parameters that will be appended to the wrapped function's signature. Default is [].

    Returns:
       Callable[TParams, TReturnType]: The wrapped function as a coroutine
    """

    callable_types = get_callable_types(
        func,
    )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    @wraps(func, append_args=append_args)
    async def wrapper(*args: TParams.args, **kwargs: TParams.kwargs) -> TReturnType:

        bound_args = args
        bound_kwargs = kwargs

        for param in append_args:
            bound_kwargs.pop(param.name)

        bound_params: BoundArguments = callable_types.sig.bind(
            *bound_args, **bound_kwargs
        )

        for param_name, param_value in bound_params.arguments.items():

            bound_params.arguments[param_name] = convert_value_to_type(
                param_value, callable_types.parameters[param_name].annotation
            )

        bound_params.apply_defaults()

        if pre_hooks:
            for pre_hook in pre_hooks:
                async_pre_hook = make_async(pre_hook)
                bound_params = await async_pre_hook(
                    bound_params, callable_types, config, *args, **kwargs
                )

        wrapper.validate(*bound_params.args, **bound_params.kwargs)

        async_func = make_async(func)

        result: TReturnType = await async_func(
            *bound_params.args, **bound_params.kwargs
        )

        if post_hooks:

            for post_hook in post_hooks:

                async_post_hook = make_async(post_hook)

                result = await async_post_hook(
                    result, callable_types, config, *args, **kwargs
                )

        return result

    wrapper.is_action = True

    return wrapper


# Objects


def add_attr_to_class(
    cls: TType,
    name: str,
    default: Any | None | Parameter.empty = Parameter.empty,
    annotation: Any | Parameter.empty = Parameter.empty,
) -> TType:

    setattr(cls, name, default)

    if not default == Parameter.empty and not annotation == Parameter.empty:
        cls.__annotations__[name] = annotation

    return cls
