import loguru
from pydantic import BaseModel
from kitman import Plugin, Kitman
from loguru import Logger

from kitman.kitman import InstallableManager


class LoguruConf(BaseModel):

    enable: bool = True


class LoguruPluginManager(InstallableManager["LoguruPlugin", LoguruConf]):

    default_conf = LoguruConf()


class LoguruPlugin(Plugin[LoguruConf]):

    name = "Loguru"
    description = "A plugin that provides a loguru logger dependency"
    manager = LoguruPluginManager()

    def get_logger(self) -> Logger:

        logger = Logger()

        if self.conf.enable:
            logger.enable("kitman")
        else:
            logger.disable("kitman")
        return logger
