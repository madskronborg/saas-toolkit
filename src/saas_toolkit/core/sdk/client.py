import inspect
from typing import Generic, Optional, TypeVar, Union, get_type_hints


from httpx import AsyncClient, Client as HTTPXClient
from httpx import AsyncClient as HTTPXAsyncClient

TClient = TypeVar("TClient")
TClientExtension = TypeVar("TClientExtension", bound="BaseClient")


class BaseClient(Generic[TClient, TClientExtension]):

    parent: Optional[TClient | TClientExtension] = None
    client: Optional[TClient] = None

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._connect_extensions()

    def _get_extensions(
        self,
    ) -> dict[str, Union["ClientExtension", "AsyncClientExtension"]]:

        attrs = get_type_hints(self)

        extensions: dict[str, ClientExtension | AsyncClientExtension] = {}

        for name, value in attrs.items():

            if not inspect.isclass(value):
                continue

            if issubclass(value, (ClientExtension, AsyncClientExtension)):
                extensions[name] = value

        return extensions

    def _bind(self, extension: TClientExtension) -> None:

        extension.parent = self

        if isinstance(self, (Client, AsyncClient)):
            setattr(extension, "client", self)
        else:
            setattr(extension, "client", self.client)

    def _connect_extensions(self) -> None:

        extensions = self._get_extensions()

        for name, extension_cls in extensions.items():

            extension = extension_cls()

            setattr(self, name, extension)

            self._bind(extension)


class ClientExtension(BaseClient["Client", "ClientExtension"]):
    pass


class Client(BaseClient["Client", "ClientExtension"], HTTPXClient):
    pass


class AsyncClientExtension(BaseClient["AsyncClient", "AsyncClientExtension"]):
    pass


class AsyncClient(BaseClient["AsyncClient", "AsyncClientExtension"], HTTPXAsyncClient):
    pass
