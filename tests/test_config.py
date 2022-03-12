from fastapi import FastAPI
import pytest
from .types import CONFIG
from src.saas_toolkit.config import Settings


def test_configuration(app: FastAPI, configuration: CONFIG):

    configure, SETTINGS = configuration

    assert SETTINGS is None, "Settings are not empty!"

    configure({})

    assert SETTINGS is not None
