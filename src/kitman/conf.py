from typing import Optional, Type
from databases import Database
from pydantic import BaseModel
from sqlalchemy import MetaData
from .logging import logger
from deepmerge import always_merger
from kitman import errors


class BaseSettings(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True


class SQLSettings(BaseSettings):
    metadata: Optional[MetaData] = None
    database: Optional[Database] = None


class LoggingSettings(BaseSettings):

    enable: bool = False


class Settings(BaseSettings):

    sql: SQLSettings = SQLSettings()
    logging: LoggingSettings = LoggingSettings()


SETTINGS: Settings = Settings()


def configure(user_settings: Settings | dict, partial: bool = False) -> None:
    new_settings: Optional[dict] = None

    logger.info("User Settings are:", user_settings, "Partial:", partial)

    if not partial:

        if isinstance(user_settings, dict):
            new_settings = user_settings
        else:
            new_settings = user_settings.dict()

    if partial:

        if isinstance(user_settings, dict):
            new_settings = always_merger.merge(SETTINGS.dict(), user_settings)
        else:
            new_settings = always_merger.merge(SETTINGS.dict(), user_settings.dict())

    if new_settings == None:
        raise ValueError("new_settings are not set!")

    for key, value in new_settings.items():

        setattr(SETTINGS, key, value)

    # Logging
    if SETTINGS.logging.enable:
        logger.enable("kitman")
    else:
        logger.disable("kitman")
