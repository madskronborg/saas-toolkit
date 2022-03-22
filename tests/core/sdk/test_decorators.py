import inspect
from typing import Optional
from saas_toolkit.core.sdk.decorators import (
    get_params,
    get_request_data,
    get_response_data,
)
from saas_toolkit.core import sdk


def test_get_params():
    class TestParams(sdk.Params):

        userId: int

    def optional_params(params: Optional[TestParams]) -> None:
        pass

    optional_params_sig = inspect.signature(optional_params)

    def required_params(params: TestParams) -> None:
        pass

    required_params_sig = inspect.signature(required_params)

    # Test optional params without params
    assert (
        get_params(optional_params_sig, None) == None
    ), "get_params does not support Optional[Params]"

    # Test optional params with dict
    optional_test_params = get_params(optional_params_sig, params={"userId": 0})
    assert isinstance(
        optional_test_params, TestParams
    ), "get_params does not convert dict to pydantic model"
    assert (
        optional_test_params.userId == 0
    ), "get_params does not pass dict data to Params model correctly"
