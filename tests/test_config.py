from fastapi import FastAPI
from saas_toolkit.config import Settings, configure, SETTINGS
from saas_toolkit import logger


def test_configuration(app: FastAPI):

    assert SETTINGS == Settings(), "Settings does not have a default value"

    configure({})

    assert SETTINGS != None, "Settings are not updated"


def test_logging_config(app: FastAPI):

    logger.info("You can't see me")

    assert SETTINGS.logging.enable == False, "Logging is not disabled by default"

    configure(dict(logging=dict(enable=True)), partial=True)

    assert SETTINGS.logging.enable == True, "Logging settings are not updated"

    logger.info("You can see me")
