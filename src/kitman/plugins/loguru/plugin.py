import loguru
from kitman import Plugin, Kitman
from loguru import Logger


class LoguruPlugin(Plugin):

    name = "Loguru"
    description = "A plugin that provides a loguru logger dependency"

    def get_logger(self) -> Logger:

        logger = Logger()

        if self.kitman.settings.logging.enable:
            logger.enable("kitman")
        else:
            logger.disable("kitman")
        return logger
