from typing import Optional, Type
from pydantic import BaseModel
from sqlalchemy import MetaData
from .logging import logger
from deepmerge import always_merger
from saas_toolkit import errors


class DatabaseSettings(BaseModel):
    metadata: Optional[MetaData] = None


class LoggingSettings(BaseModel):

    enable: bool = True


class Settings(BaseModel):

    database: DatabaseSettings = DatabaseSettings()
    logging: LoggingSettings = LoggingSettings()


SETTINGS: Optional[Settings] = None


def configure(user_settings: Settings | dict, partial: bool = False) -> None:
    global SETTINGS

    if not partial:

        if isinstance(user_settings, dict):
            SETTINGS = Settings(**user_settings)
        else:
            SETTINGS = user_settings

    if partial:

        if not isinstance(user_settings, dict):
            raise errors.ConfigurationError(
                "When using configure() with partial=True the provided object must be a dict"
            )

        if SETTINGS:
            SETTINGS = Settings(**always_merger(SETTINGS.dict(), user_settings))
        else:
            SETTINGS = Settings(**user_settings)

    # Logging
    if SETTINGS.logging.enable:
        logger.enable("saas_toolkit")
    else:
        logger.disable("saas_toolkit")
