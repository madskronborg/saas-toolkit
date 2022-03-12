from fastapi import FastAPI
import pytest
from saas_toolkit.config import Settings, configure, SETTINGS


def test_configuration(app: FastAPI):

    assert SETTINGS == Settings(), "Settings does not have a default value"

    configure({})

    assert SETTINGS != None, "Settings are not updated"


def test_logging_config(app: FastAPI):

    assert SETTINGS.logging.enable == False, "Logging is not disabled by default"

    configure(dict(logging=dict(enable=True)), partial=True)

    assert SETTINGS.logging.enable == True, "Logging settings are not updated"
