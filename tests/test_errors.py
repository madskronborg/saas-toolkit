from fastapi import FastAPI
from kitman import exceptions


def test_error():

    assert (
        exceptions.HTTPError(message="My Error").message == "My Error"
    ), "String message not set"

    assert exceptions.HTTPError(message=0).message == 0, "Int message not set"

    assert exceptions.HTTPError(message={"detail": "My Message"}).message == {
        "detail": "My Message"
    }, "Dictionary message not set"

    assert exceptions.HTTPError(message=["Error 1", "Error 2"]).message == [
        "Error 1",
        "Error 2",
    ], "List message not set"
