from typing import Generic, TypeVar

from fastapi import FastAPI, Request
from pydantic import BaseModel, BaseSettings
from pydantic.generics import GenericModel
from fastapi.responses import JSONResponse

from kitman import errors

from .conf import Settings
from __future__ import annotations

TKitmanSettings = TypeVar("TKitmanSettings", bound=Settings)
TInstallableConf = TypeVar("TInstallableConf", bound=BaseSettings | BaseModel)
TInstallable = TypeVar("TInstallable", bound="Installable")


class InstallableError(Exception):
    pass


class InstallableManager(GenericModel, Generic[TInstallable, TInstallableConf]):

    default_conf: TInstallableConf | None = None
    require_conf: bool = False

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
    def conf(self) -> TInstallableConf:

        return self.parent.conf

    def install(self, kitman: Kitman, conf: TInstallableConf | None = None) -> None:
        self.parent.kitman = kitman
        self.parent.conf = conf or self.default_conf

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

        if self.require_conf:

            if not self.parent.conf:
                self.fail(f"No config provided but config is required")

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


class Installable(Generic[TInstallableConf]):
    name: str
    description: str
    kitman: Kitman | None = None
    conf: TInstallableConf | None = None
    manager: InstallableManager = InstallableManager()

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.manager.parent = self


class Plugin(Installable[TInstallableConf]):
    pass


class Kit(Plugin[TInstallableConf]):
    pass


class Kitman(Plugin, Generic[TKitmanSettings]):

    fastapi: FastAPI
    settings: Settings
    kits: dict[type[Kit], Kit] = {}

    def __init__(self, fastapi: FastAPI, settings: Settings):

        self.fastapi = fastapi
        self.settings = settings

        self.fastapi.title = settings.project_name
        self.fastapi.add_exception_handler(errors.HTTPError, self.exception_handler)

    def use(
        self, installable: Plugin | Plugin, conf: BaseSettings | BaseModel | None = None
    ) -> None:

        installable_type = type(installable)

        installable.manager.install(self, conf)

        installable.manager.check()

        if isinstance(installable, Plugin):
            self.kits[installable_type] = installable

        else:
            self.manager.plugins[installable_type] = installable

    async def exception_handler(
        self, request: Request, exc: errors.HTTPError
    ) -> JSONResponse:

        data = dict(
            status_code=exc.status_code,
        )

        content: dict = dict(detail=exc.message, code=exc.code)

        data["content"] = content

        return JSONResponse(**data)
