from inspect import BoundArguments, signature, Signature, Parameter, isawaitable
from typing import Any, Callable, ParamSpec, Type, TypeVar, Literal
from pydantic import parse_obj_as, validate_arguments
from makefun import wraps
from collections import OrderedDict
from dataclasses import dataclass
from collections.abc import Coroutine

from concurrent.futures import ThreadPoolExecutor
import asyncio


TAnnotation = TypeVar("TAnnotation")
TType = TypeVar("TType", bound=Type)
TParams = ParamSpec("TParams")
TReturnType = TypeVar("TReturnType")
TActionOrignalFunc = Callable[TParams, TReturnType | Coroutine[None, None, TReturnType]]
TActionWrappedFunc = Callable[TParams, Coroutine[None, None, TReturnType]]


@dataclass
class CallableTypes:

    parameters: OrderedDict[str, Parameter]
    return_type: Any
    sig: Signature


# Callables
def make_async(
    func: Callable[TParams, TReturnType | Coroutine[None, None, TReturnType]]
) -> Callable[TParams, Coroutine[None, None, TReturnType]]:
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

        if isawaitable(func):
            return func(*args, **kwargs)

        future = pool.submit(func, *args, **kwargs)

        return asyncio.wrap_future(future)

    return wrapper


def get_callable_types(
    func: Callable[TParams, TReturnType], include_self: bool = False
) -> CallableTypes:

    sig = signature(func, eval_str=True)

    parameters: OrderedDict[str, Parameter] = OrderedDict(**sig.parameters)

    if not include_self:
        if "self" in parameters:
            parameters.pop("self")

    return CallableTypes(
        parameters=parameters, return_type=sig.return_annotation, sig=sig
    )


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

    if isinstance(value, annotation):
        return value

    return parse_obj_as(annotation, value)


def action(
    pre_hooks: list[
        Callable[
            [BoundArguments, CallableTypes],
            BoundArguments | Coroutine[None, None, BoundArguments],
        ]
    ] = [],
    post_hooks: list[
        Callable[
            [TReturnType, CallableTypes],
            TReturnType | Coroutine[None, None, TReturnType],
        ]
    ] = [],
) -> Callable[[TActionOrignalFunc], TActionWrappedFunc]:
    """
    action

    Decorates a function as an action.
    Actions are characterized by:

    - Arguments are type validated
    - Result will always be a coroutine
    - Supports pre_hooks to manipulate arguments and keyword arguments before calling the wrapped function
    - Supports post_hooks to alter the result of calling the wrapped functions

    IMPORTANT

    `pre_hooks` and `post_hooks` are called in order, therefore, any alterations you make in a previous hook will be present in the following hooks.

    Args:
        pre_hooks (list[ Callable[ [BoundArguments, CallableTypes], BoundArguments  |  Coroutine[None, None, BoundArguments], ] ], optional): A list of functions that can alter arguments and keyword arguments that will be passed to the wrapped function. Defaults to [].
        post_hooks (list[ Callable[ [TReturnType, CallableTypes], TReturnType  |  Coroutine[None, None, TReturnType], ] ], optional): A list of functions that can alter the result of calling the wrapped function. Defaults to [].

    Returns:
        Callable[ [Callable[TParams, TReturnType | Coroutine[None, None, TReturnType]]], Callable[TParams, Coroutine[None, None, TReturnType]], ]: The wrapped function that returns a coroutine
    """

    def decorator(func: TActionOrignalFunc) -> TActionWrappedFunc:

        callable_types = get_callable_types(func)

        @validate_arguments
        @wraps(func)
        async def wrapper(*args: TParams.args, **kwargs: TParams.kwargs) -> TReturnType:

            bound_params: BoundArguments = callable_types.sig.bind(*args, **kwargs)

            for param_name, param_value in bound_params.arguments.items():

                bound_params.arguments[param_name] = convert_value_to_type(
                    param_value, callable_types.parameters[param_name].annotation
                )

            bound_params.apply_defaults()

            if pre_hooks:
                for pre_hook in pre_hooks:
                    bound_params = await make_async(pre_hook)(
                        bound_params, callable_types
                    )

            wrapper.validate(*bound_params.args, **bound_params.kwargs)

            result: TReturnType = await make_async(func)(
                *bound_params.args, **bound_params.kwargs
            )

            if post_hooks:

                for post_hook in post_hooks:

                    result = await make_async(post_hook)(result, callable_types)

            return result

        wrapper.is_action = True

        return wrapper

    return decorator


@action
def test_action(name: str) -> str:

    return ""


test_action()

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
