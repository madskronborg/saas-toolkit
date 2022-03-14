import databases
import pytest

from starlette.testclient import TestClient
import sqlalchemy
from fastapi import FastAPI
from saas_toolkit import configure
from saas_toolkit.conf import Settings
from . import variables

metadata = variables.METADATA
database = variables.DATABASE

test_settings = Settings(sql=dict(metadata=metadata, database=database))

configure(test_settings)

# Configuration
@pytest.fixture(scope="module", autouse=True)
def configuration():

    configure(test_settings)

    yield

    # Reset configuration
    configure(test_settings)


# App
@pytest.fixture(scope="module")
def app() -> FastAPI:

    return FastAPI()


# Database


@pytest.fixture(scope="module")
def db():

    engine = sqlalchemy.create_engine(variables.DATABASE_URL)
    metadata.drop_all(engine)
    metadata.create_all(engine)
    yield database
    metadata.drop_all(engine)
    configure(test_settings)


# Client
@pytest.fixture(scope="module")
def client(app: FastAPI):
    with TestClient(app) as client:
        yield client
