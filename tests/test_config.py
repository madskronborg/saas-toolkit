import databases
from fastapi import FastAPI
import sqlalchemy
from kitman.conf import Settings, configure, settings
from kitman import logger
from . import variables


def test_configuration():

    configure(Settings())

    assert settings == Settings(), "Settings does not have a default value"

    configure({})

    assert settings != None, "Settings are not updated"


def test_logging_config():

    logger.info("You can't see me")

    assert settings.logging.enable == False, "Logging is not disabled by default"

    configure(dict(logging=dict(enable=True)), partial=True)

    assert settings.logging.enable == True, "Logging settings are not updated"

    logger.info("You can see me")


def test_sql_settings():

    assert settings.sql.metadata == None, "Metadata is not None as default"
    assert settings.sql.database == None, "Database is not None as default"

    metadata = sqlalchemy.MetaData()
    database = databases.Database(variables.DATABASE_URL)

    configure(
        {
            "sql": {
                "metadata": metadata,
                "database": database,
            }
        }
    )

    assert settings.sql.metadata == metadata, "sql.metadata is not updated"
    assert settings.sql.database == database, "database is not updated"
