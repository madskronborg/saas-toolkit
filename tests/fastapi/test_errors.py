from fastapi import FastAPI, Request
from saas_toolkit import errors
from saas_toolkit.fastapi.conf import setup as fastapi_setup
from starlette.testclient import TestClient


def test_exception_handler(app: FastAPI, client: TestClient):

    fastapi_setup(app)

    @app.route("/", ["get"])
    async def index(request: Request):

        raise errors.Error("Some error")

    response = client.get("/")

    assert response.status_code == 400, "Default error status_code is not 400"
    assert response.json() == {
        "detail": "Some error",
        "code": None,
    }, "Error response content is not set"
