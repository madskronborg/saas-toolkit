from typing import Generic, TypeVar

from fastapi import FastAPI

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


class App(Installable):

    plugins: dict[type[Plugin], Plugin] = {}


class Kitman(App, Generic[TSettings]):

    fastapi: FastAPI
    settings: Settings
    apps: dict[type[App], App] = {}

    def __init__(self, fastapi: FastAPI, settings: Settings):

        self.fastapi = fastapi
        self.settings = settings

    def use(self, installable: App | Plugin) -> None:

        installable.install(self)

        installable._check()

        if isinstance(installable, App):
            self.apps[installable] = installable

        else:
            self.plugins[installable] = installable


class App(Installable):

    plugins: dict[type[Plugin], Plugin] = {}


class Plugin(Installable):

    pass
