import inspect
from typing import Optional, TypeVar

from pydantic import AnyHttpUrl, BaseModel
from . import request, response

from httpx import Client as HTTPXClient
from httpx import AsyncClient as HTTPXAsyncClient

TRequest = TypeVar("TRequest", bound=request.Request)
TResponse = TypeVar("TResponse", bound=response.Response)


class BaseClient:

    parent: Optional["Client" | "ClientExtension"] = None
    client: "Client"

    def _get_extensions(self) -> list["ClientExtension"]:

        extensions = inspect.getmembers(
            self,
            predicate=lambda o: inspect.isclass(o) and isinstance(o, ClientExtension),
        )

        return extensions

    def bind(self, extension: "ClientExtension") -> None:

        extension.parent = self

        if isinstance(self, Client):
            extension.client = self
        else:
            extension.client = self.client


class ClientExtension(BaseClient):
    pass


class Client(HTTPXClient, BaseClient):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        extensions = self._get_extensions()

        for extension in extensions:
            self.bind(extension)


class AsyncClient(HTTPXAsyncClient, BaseClient):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        extensions = self._get_extensions()

        for extension in extensions:
            self.bind(extension)
