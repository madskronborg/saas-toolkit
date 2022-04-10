from typing import Callable, Coroutine
from typing_extensions import reveal_type

from saas_toolkit.core.schemas import Schema
from saas_toolkit.core import dynamic
import inspect
from collections import OrderedDict
from makefun import wraps

# Callables
async def test_make_async():
    def sync_func(param: str) -> str:
        return param

    async def async_func(param: str) -> Coroutine[None, None, str]:
        return param

    # Test sync
    sync_func_as_async = dynamic.make_async(sync_func)

    assert inspect.iscoroutinefunction(
        sync_func_as_async
    ), "make_async does not convert sync to async"

    assert (
        await sync_func_as_async("param") == "param"
    ), "make_async does not return sync -> async function with correct params"

    # Test async

    async_func_as_async = dynamic.make_async(async_func)

    assert inspect.iscoroutinefunction(
        async_func_as_async
    ), "make_async does not recognize already async functions"

    assert (
        await async_func_as_async("param") == "param"
    ), "make_async does not return async -> async function with correct params"


def test_get_callable_types():
    def func(param1: str, param2: int) -> str | int:

        return param1 or param2

    # Without include_self
    def test_without_self():
        callable_types = dynamic.get_callable_types(func)

        assert (
            callable_types.return_type == str | int
        ), "get_callable_types return_type is wrong"

        assert isinstance(
            callable_types.parameters, OrderedDict
        ), "Parameters is not an instance of OrderedDict"

        for key in ["param1", "param2"]:

            assert (
                key in callable_types.parameters
            ), "parameters does not include all parameters"

        assert callable_types.sig == inspect.signature(
            func
        ), "sig is not the signature of provided function"

    test_without_self()

    # With include_self
    class Obj:
        def meth(self, x: str) -> str:
            return x

    def test_with_self():

        callable_types = dynamic.get_callable_types(Obj.meth, include_self=True)

        assert "self" in callable_types.parameters, "self is not included in parameters"

    test_with_self()


def test_convert_value_to_type():

    assert (
        dynamic.convert_value_to_type("1", int) == 1
    ), "Convert failed to convert string to int"

    assert (
        dynamic.convert_value_to_type(None, str | None) == None
    ), "convert_value_to_type does not work with type aliases"


async def test_make_action():
    def action(
        func: Callable[dynamic.TParams, Coroutine[None, None, dynamic.TReturnType]]
    ):
        def log_args(
            params: inspect.BoundArguments,
            callable_types: dynamic.CallableTypes,
            config: None,
            *args,
            **kwargs
        ) -> inspect.BoundArguments:

            print("Params are:", str(params))

            return params

        async def log_result_to_server(
            result: dynamic.TReturnType,
            callable_types: dynamic.CallableTypes,
            config: None,
            *args,
            **kwargs
        ):

            # Make async request to server ...

            return result

        return dynamic.make_action(
            func, pre_hooks=[log_args], post_hooks=[log_result_to_server]
        )

    class TestSchema(Schema):

        name: str
        family_names: list[str] = []

    @action
    async def wrapped_func(
        param1: str, param2: dict, param3: TestSchema, foo: str | None
    ) -> str | dict | TestSchema:

        return param1 or param2 or param3

    # Test async conversion
    # assert inspect.iscoroutinefunction(
    #    wrapped_func
    # ), "make_action does not convert func to async"

    # Test argument conversion
    result = await wrapped_func(
        "", {}, {"name": "Test", "family_names": ["foo", "bar"]}, foo="bar"
    )

    result == TestSchema(
        name="Test", family_names=["foo", "bar"]
    ), "make_action does not convert parameters to specified type"
