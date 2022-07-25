from typing import Generic, TypeVar

from fastapi import FastAPI
from pydantic import BaseModel

from .conf import Settings
from __future__ import annotations

TSettings = TypeVar("TSettings", bound=Settings)


class InstallableError(Exception):
    pass


class Installable:
    name: str
    description: str
    kitman: Kitman | None = None

    @property
    def ready(self) -> bool:
        return self._check(raise_exception=False)

    def install(self, kitman: Kitman) -> None:
        self.kitman = kitman

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

    def _check(self, raise_exception: bool = True) -> bool:
        """
        check

        Use this to run checks that verify the plugin or app is functional

        Args:
            raise_exception (bool): Raise an error message instead of returning a bool. Defaults to True

        Raises:
            InstallableError: An Installable error
        """

        if self.kitman is None:
            if raise_exception:
                self.fail(
                    "Kitman is not set. Have you installed it by calling the .use() method on a kitman instance?"
                )

            return False

        return True


class Plugin(Installable):
    class Config:
        required_plugins = list[tuple[str, set[type["Plugin"]]]] = []

    @property
    def config(self) -> Config:

        return self.Config()

    plugins: dict[type[Plugin], Plugin] = {}

    def _check(self, raise_exception: bool = True) -> bool:
        valid = super()._check(raise_exception)

        if self.config.required_plugins:

            installed_plugins = self.plugins.values()

            for plugin_config in self.config.required_plugins:

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

        return valid


class Kit(Plugin):

    pass


class Kitman(Kit, Generic[TSettings]):

    fastapi: FastAPI
    settings: Settings
    kits: dict[type[Kit], Kit] = {}

    def __init__(self, fastapi: FastAPI, settings: Settings):

        self.fastapi = fastapi
        self.settings = settings

    def use(self, installable: Kit | Plugin) -> None:

        installable_type = type(installable)

        installable.install(self)

        installable._check()

        if isinstance(installable, Kit):
            self.kits[installable_type] = installable

        else:
            self.plugins[installable_type] = installable
