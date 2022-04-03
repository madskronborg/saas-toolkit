from inspect import signature, Signature, Parameter
from typing import Any, Callable, Type, TypeAlias, TypeVar, TypedDict, cast

TType = TypeVar("TType", bound=Type)

# Callables
def get_callable_types(
    func: Callable | Signature, include_self: bool = False
) -> tuple[list[Parameter], Any]:

    sig: Signature | None = None

    if isinstance(func, Signature):
        sig = func

    else:
        sig = signature(func, eval_str=True)

    parameters: list[Parameter] = []

    for name, parameter in sig.parameters.items():

        if name == "self":
            if not include_self:
                continue

        parameters.append(parameter)

    return (
        parameters,
        sig.return_annotation,
    )


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
