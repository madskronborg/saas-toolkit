import loguru
from kitman import Plugin, Kitman
from loguru import logger, Logger


class LoguruPlugin(Plugin):

    name = "Loguru Plugin"
    description = "A plugin that provides a loguru logger dependency"

    def get_logger(self) -> Logger:

        if self.kitman.settings.logging.enable:
            logger.enable()
        else:
            logger.disable()
        return logger
