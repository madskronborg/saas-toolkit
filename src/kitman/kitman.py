from __future__ import annotations

from typing import Generic, Protocol, TypeVar, overload

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from kitman import exceptions
from kitman.core.commands import Command, CommandHandler, TCommandHandler
from kitman.core.events import BaseEmitter, DomainEvent, EventHandler
from kitman.core.queries import Query, QueryHandler, TQueryHandler

from .conf import Settings
from pydantic_settings import BaseSettings

TKitmanSettings = TypeVar("TKitmanSettings", bound=Settings)
TInstallableSettings = TypeVar(
    "TInstallableConf", bound=BaseSettings | BaseModel | None
)
TInstallable = TypeVar("TInstallable", bound="Installable")


class InstallableError(Exception):
    pass


class InstallableManager(BaseModel, Generic[TInstallable, TInstallableSettings]):

    default_settings: TInstallableSettings | None = None
    require_settings: bool = False

    parent: TInstallable | Installable | None = None

    plugins: dict[type[Plugin], Plugin] = []
    required_plugins: list[tuple[str, set[type["Plugin"]]]] = []

    @property
    def ready(self) -> bool:
        return self.check(raise_exception=False)

    @property
    def kitman(self) -> TInstallable:

        return self.parent.kitman

    @property
    def settings(self) -> TInstallableSettings:

        return self.parent.settings

    def install(
        self, kitman: Kitman, settings: TInstallableSettings | None = None
    ) -> None:
        self.parent.kitman = kitman
        self.parent.settings = settings or self.default_settings

    def fail(self, message: str, *args, **kwargs) -> None:
        """
        fail

        Utility function for raising InstallableError(s)

        Args:
            message (str): An error message

        Raises:
            InstallableError: An Installable error
        """

        raise InstallableError(message, *args, **kwargs)

    def check(self, raise_exception: bool = True) -> bool:
        """
        check

        Use this to run checks that verify the plugin or app is functional

        Args:
            raise_exception (bool): Raise an error message instead of returning a bool. Defaults to True

        Raises:
            InstallableError: An Installable error
        """

        if self.parent.kitman is None:
            if raise_exception:
                self.fail(
                    "Kitman is not set. Have you installed it by calling the .use() method on a kitman instance?"
                )

            return False

        if self.require_settings:

            if not self.parent.settings:
                self.fail(f"Settings are required")

        if self.required_plugins:

            installed_plugins = self.plugins()

            for plugin_config in self.required_plugins:

                plugin_config_valid: bool = False

                for required_plugin in plugin_config[1]:

                    if required_plugin in installed_plugins:
                        plugin_config_valid = True
                        break

                if not plugin_config_valid:

                    if raise_exception:
                        self.fail(
                            f"{self.__class__.__name__} is missing required plugin for {plugin_config[0]}"
                        )
                    else:
                        return False

        # Default to True
        return True

    def get_plugin(self, name: str) -> Plugin | None:

        for plugin_config in self.required_plugins:

            if not plugin_config[0] == name:
                continue

            for plugin_type in plugin_config[1]:

                if plugin_type in self.plugins:
                    return self.plugins[plugin_type]

        return None

    def add_plugin(self, plugin: Plugin) -> None:

        self.plugins[type(plugin)] = plugin


TInstallableManager = TypeVar("TInstallableManager", bound=InstallableManager)


class Installable(Generic[TInstallableSettings]):
    name: str
    description: str
    kitman: Kitman | None = None
    settings: TInstallableSettings | None = None
    manager: InstallableManager = InstallableManager()

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.manager.parent = self


class Plugin(Installable[TInstallableSettings]):
    pass


class Kit(Plugin[TInstallableSettings]):
    pass


class Kitman(Plugin, Generic[TKitmanSettings]):

    api: FastAPI
    settings: Settings
    emitter: BaseEmitter | None = None
    kits: dict[type[Kit], Kit] = {}

    provides: dict[
        type[CommandHandler] | type[QueryHandler] | Protocol,
        CommandHandler | QueryHandler,
    ] = {}
    events: dict[type[DomainEvent] | Protocol, set[EventHandler]] = {}

    def __init__(self, settings: Settings, emitter: BaseEmitter | None = None):

        self.settings = settings

        if emitter:
            emitter.bind(self)
            self.emitter = emitter

    def use(
        self,
        installable: FastAPI | Plugin | Kit,
        settings: BaseSettings | BaseModel | None = None,
    ) -> None:

        if isinstance(installable, FastAPI):
            self.api = installable
            self.api.title = self.settings.project_name
            self.api.add_exception_handler(exceptions.HTTPError, self.exception_handler)
            return

        installable_type = type(installable)

        installable.manager.install(self, settings)

        installable.manager.check()

        if isinstance(installable, Plugin):
            self.kits[installable_type] = installable

        else:
            self.manager.plugins[installable_type] = installable

    # Domain Driven Design
    async def emit(self, event: DomainEvent):
        await self.emitter.emit(event)

    def event(self, handler: EventHandler):
        handler.kitman = self

        for event_type in handler.handles:

            self.events.setdefault(event_type, set())

            self.events[event_type].add(handler)

    def command(self, handler: CommandHandler, token: Protocol | None = None):
        handler.kitman = self
        self.provides[type(handler)] = handler

        if token:
            self.provides[token] = handler

    def query(self, handler: QueryHandler, token: Protocol | None = None):
        handler.kitman = self
        self.provides[type(handler)] = handler

        if token:
            self.provides[token] = handler

    def provide(
        self, handler: CommandHandler | QueryHandler, token: Protocol | None = None
    ):

        handler.kitman = self

        if isinstance(handler, CommandHandler):
            self.command(handler, token)

        if isinstance(handler, QueryHandler):
            self.query(handler, token)

    @overload
    def inject(self, token: type[TQueryHandler]) -> TQueryHandler:
        ...

    @overload
    def inject(self, token: type[TCommandHandler]) -> TCommandHandler:
        ...

    def inject(self, token: type[TQueryHandler] | type[TCommandHandler] | Protocol):

        handler = self.provides.get(token, None)

        if not handler:
            raise ValueError("Kitman does not provide:", token)

        return handler

    # End domain driven design

    async def exception_handler(
        self, request: Request, exc: exceptions.HTTPError
    ) -> JSONResponse:

        data = dict(
            status_code=exc.status_code,
        )

        content: dict = dict(detail=exc.message, code=exc.code)

        data["content"] = content

        return JSONResponse(**data)
