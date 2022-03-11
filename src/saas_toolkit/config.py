from typing import Optional, Type
from pydantic import BaseModel
from sqlalchemy import MetaData
from .logging import logger
from deepmerge import always_merger
from saas_toolkit import errors


class DatabaseSettings(BaseModel):
    metadata: Type[MetaData]


class LoggingSettings(BaseModel):

    enable: bool = True


class Settings(BaseModel):

    database: DatabaseSettings
    logging: LoggingSettings = LoggingSettings()


settings: Optional[Settings] = None


def configure(user_settings: Settings | dict, partial: bool = False) -> None:
    global settings

    if not partial:

        if isinstance(user_settings, dict):
            settings = Settings(**user_settings)
        else:
            settings = user_settings

    if partial:

        if not isinstance(user_settings, dict):
            raise errors.ConfigurationError(
                "When using configure() with partial=True the provided object must be a dict"
            )

        if settings:
            settings = Settings(**always_merger(settings.dict(), user_settings))
        else:
            settings = Settings(**user_settings)

    # Logging
    if settings.logging.enable:
        logger.enable("saas_toolkit")
    else:
        logger.disable("saas_toolkit")
