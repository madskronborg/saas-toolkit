from fastapi import FastAPI
from kitman import errors


def test_error():

    assert (
        errors.HTTPError(message="My Error").message == "My Error"
    ), "String message not set"

    assert errors.HTTPError(message=0).message == 0, "Int message not set"

    assert errors.HTTPError(message={"detail": "My Message"}).message == {
        "detail": "My Message"
    }, "Dictionary message not set"

    assert errors.HTTPError(message=["Error 1", "Error 2"]).message == [
        "Error 1",
        "Error 2",
    ], "List message not set"
