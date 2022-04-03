import inspect
from typing import Optional
from saas_toolkit.core.sdk.decorators import (
    get_params,
    get_request_data,
    get_response_data,
)
from saas_toolkit.core import sdk


def test_get_params():
    class TestParams(sdk.QueryParams):

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


def test_get_request_data():
    class TestRequest(sdk.Request):

        userId: int

    class TestResponse(sdk.Response):
        userId: int
        customer: str

    def optional_params(data: Optional[TestRequest]) -> None:
        pass

    optional_params_sig = inspect.signature(optional_params)

    def required_params(data: TestRequest) -> TestResponse:

        return TestResponse(userId=data.userId, customer="Test")

    required_params_sig = inspect.signature(required_params)

    # Test no data

    assert (
        get_request_data(optional_params_sig, None) is None
    ), "get_request_data does not work with None value"

    # Test return type conversion
    response = get_request_data(required_params_sig, {"userId": 1})
    assert isinstance(
        response, TestRequest
    ), "get_request_data failed to convert response to signature data type"

    assert (
        response.userId == 1
    ), "get_request_data failed to pass data during type conversion"


def test_get_response_data():

    pass
