import databases
from fastapi import FastAPI
import sqlalchemy
from kitman.conf import Settings, configure, SETTINGS
from kitman import logger
from . import variables


def test_configuration():

    configure(Settings())

    assert SETTINGS == Settings(), "Settings does not have a default value"

    configure({})

    assert SETTINGS != None, "Settings are not updated"


def test_logging_config():

    logger.info("You can't see me")

    assert SETTINGS.logging.enable == False, "Logging is not disabled by default"

    configure(dict(logging=dict(enable=True)), partial=True)

    assert SETTINGS.logging.enable == True, "Logging settings are not updated"

    logger.info("You can see me")


def test_sql_settings():

    assert SETTINGS.sql.metadata == None, "Metadata is not None as default"
    assert SETTINGS.sql.database == None, "Database is not None as default"

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

    assert SETTINGS.sql.metadata == metadata, "sql.metadata is not updated"
    assert SETTINGS.sql.database == database, "database is not updated"
