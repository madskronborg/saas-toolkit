import sys
import databases
import pytest
from httpx import AsyncClient
from starlette.testclient import TestClient
import sqlalchemy
from fastapi import FastAPI
from saas_toolkit import configure, SETTINGS
from saas_toolkit.config import Settings
from . import variables

test_settings = Settings()

configure(test_settings)

# Configuration
@pytest.fixture(scope="module", autouse=True)
def configuration():

    configure(Settings())

    yield

    # Reset configuration
    configure(test_settings)


# App
@pytest.fixture(scope="module")
def app() -> FastAPI:

    return FastAPI()


# Database

database = databases.Database(variables.DATABASE_URL)
metadata = sqlalchemy.MetaData()


@pytest.fixture(scope="module")
def db():

    configure(Settings(sql=dict(metadata=metadata, database=database)))

    engine = sqlalchemy.create_engine(variables.DATABASE_URL)
    metadata.drop_all(engine)
    metadata.create_all(engine)
    yield
    metadata.drop_all(engine)
    configure(test_settings)


# Client
@pytest.fixture(scope="module")
def client(app: FastAPI):
    with TestClient(app) as client:
        yield client
