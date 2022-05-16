import inspect
from typing import Generic, Optional, TypeVar, Union, get_type_hints
from typing_extensions import Self


from httpx import AsyncClient as HTTPXAsyncClient
from pydantic import BaseModel

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
    ) -> dict[str, "AsyncClientExtension"]:

        attrs = get_type_hints(self)

        extensions: dict[str, AsyncClientExtension] = {}

        for name, value in attrs.items():

            if not inspect.isclass(value):
                continue

            if issubclass(value, (AsyncClientExtension)):
                extensions[name] = value

        return extensions

    def _bind(self, extension: TClientExtension) -> None:

        extension.parent = self

        if isinstance(self, (AsyncClientExtension)):
            setattr(extension, "client", self.client)
        else:
            setattr(extension, "client", self)

    def _connect_extensions(self) -> None:

        extensions = self._get_extensions()

        for name, extension_cls in extensions.items():

            extension = extension_cls()

            setattr(self, name, extension)

            self._bind(extension)


class AsyncClientExtension(BaseClient["AsyncClient", "AsyncClientExtension"]):
    pass


class AsyncHTTPClient(
    BaseClient["AsyncClient", "AsyncClientExtension"], HTTPXAsyncClient
):
    def __new__(cls: type[Self]) -> Self:
        klass = super().__new__(cls)

        def decorator(func):
            async def wrapper(*args, **kwargs):

                sig = inspect.signature(func)
                ba = sig.bind(*args, **kwargs)
                ba.apply_defaults()

                for name, value in ba.arguments.items():

                    if isinstance(value, BaseModel):
                        ba.arguments[name] = value.dict()

                result = await func(*ba.args, **ba.kwargs)

                return result

            return wrapper

        cli_method_names = ["get", "options", "head", "post", "put", "patch", "delete"]

        for method_name in cli_method_names:
            method = getattr(klass, method_name)

            method = decorator(method)

            setattr(klass, method_name, method)

        return klass
