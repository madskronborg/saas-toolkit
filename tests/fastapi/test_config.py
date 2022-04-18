import databases
from fastapi import FastAPI
from pydantic import PostgresDsn, SecretStr
import sqlalchemy
from kitman.fastapi.conf import (
    AppSettings,
    CorsSettings,
    PostgresSettings,
    setup as fastapi_setup,
)
from kitman import errors
from kitman.conf import SETTINGS
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware


def test_app_settings():

    default_settings = AppSettings(PROJECT_NAME="Test")

    assert (
        default_settings.PROJECT_NAME == "Test"
    ), "AppSettings PROJECT_NAME is not updated"
    assert (
        default_settings.ENV == "development"
    ), "AppSettings default ENV is not 'development'"

    assert isinstance(
        default_settings.SECRET, SecretStr
    ), "AppSettings SECRET is not a SecretStr"

    assert default_settings.SECRET == SecretStr(
        "JDEkd3FLMERidi4kelpuQ2tWelFsM3NuVUdiZXFGUjltMQo="
    ), "AppSettings default SECRET is not JDEkd3FLMERidi4kelpuQ2tWelFsM3NuVUdiZXFGUjltMQo="

    user_settings = AppSettings(
        PROJECT_NAME="User Test", ENV="production", SECRET="1234"
    )

    assert (
        user_settings.PROJECT_NAME == "User Test"
    ), "AppSettings PROJECT_NAME is not updated"
    assert user_settings.ENV == "production", "AppSettings ENV is not updated"

    assert isinstance(
        user_settings.SECRET, SecretStr
    ), "AppSettings SECRET is not a SecretStr"

    assert user_settings.SECRET == SecretStr(
        "1234"
    ), "AppSettings SECRET is not updated"


def test_cors_settings():

    default_settings = CorsSettings()

    assert (
        default_settings.BACKEND_CORS_ORIGINS == []
    ), "CorsSettings BACKEND_CORS_ORIGINS is not an empty list"

    assert CorsSettings(
        BACKEND_CORS_ORIGINS="http://localhost,https://127.0.0.1"
    ).BACKEND_CORS_ORIGINS == [
        "http://localhost",
        "https://127.0.0.1",
    ], "CorsSettings BACKEND_CORS_ORIGINS does not format comma-separated list"

    assert CorsSettings(
        BACKEND_CORS_ORIGINS=["http://localhost", "https://127.0.0.1"]
    ).BACKEND_CORS_ORIGINS == [
        "http://localhost",
        "https://127.0.0.1",
    ], "CorsSettings BACKEND_CORS_ORIGINS does not format list"


def test_postgres_settings():

    server = "localhost:5432"
    user = "test"
    pwd = "test_password"
    db_name = "test_db"
    user_settings = PostgresSettings(
        POSTGRES_SERVER=server,
        POSTGRES_USER=user,
        POSTGRES_PASSWORD=pwd,
        POSTGRES_DB=db_name,
    )

    assert isinstance(
        user_settings.POSTGRES_URI, PostgresDsn
    ), "PostgresSettings POSTGRES_URI is not an instance of PostgresDsn"

    assert (
        str(user_settings.POSTGRES_URI) == f"postgres://{user}:{pwd}@{server}/{db_name}"
    ), "POSTGRES_URI is not correct"


def test_setup(app: FastAPI):

    # No parameters
    fastapi_setup(app)

    assert (
        errors.Error in app.exception_handlers
    ), "Setup did not install exception handler"

    class FullSettings(AppSettings, CorsSettings, PostgresSettings):
        pass

    user_settings = FullSettings(
        PROJECT_NAME="Test",
        BACKEND_CORS_ORIGINS="http://localhost,https://localhost",
        POSTGRES_SERVER="localhost:5432",
        POSTGRES_USER="test",
        POSTGRES_PASSWORD="test_password",
        POSTGRES_DB="test_db",
    )

    # Settings only
    fastapi_setup(app, user_settings=user_settings)

    ## Test title is set
    assert app.title == user_settings.PROJECT_NAME, "App title not updated"

    print("Metadata is:", SETTINGS.sql.metadata)
    ## Test database
    assert isinstance(
        SETTINGS.sql.metadata, sqlalchemy.MetaData
    ), "sql metadata not set"
    assert isinstance(SETTINGS.sql.database, databases.Database), "sql database not set"

    len(app.router.on_startup) == 1, "Database startup function not registered"
    len(app.router.on_shutdown) == 1, "Database shutdown function not registered"

    # Test middleware
    assert any(
        [middleware.cls == CORSMiddleware for middleware in app.user_middleware]
    ), "CorsMiddleware not registered"
