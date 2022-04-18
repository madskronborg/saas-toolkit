from typing import Any, Optional
import databases
from fastapi import FastAPI
from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, SecretStr, validator
from typing import Optional
from .database import init_db, start_database, stop_database
from databases import Database
from kitman import errors
from sqlalchemy import MetaData
from kitman.conf import configure, SETTINGS
from fastapi.middleware.cors import CORSMiddleware
from .errors import exception_handler
from kitman.core.converters import convert_value_to_list


class AppSettings(BaseSettings):

    PROJECT_NAME: str
    ENV: str = "development"
    SECRET: SecretStr = "JDEkd3FLMERidi4kelpuQ2tWelFsM3NuVUdiZXFGUjltMQo="

    class Config:
        case_sensitive = True


class CorsSettings(BaseSettings):

    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    # Validators
    _assemble_cors_origins = validator("BACKEND_CORS_ORIGINS", pre=True)(
        convert_value_to_list
    )


class PostgresSettings(BaseSettings):

    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_USER: Optional[str]
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_URI: Optional[PostgresDsn] = None

    @validator("POSTGRES_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgres",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )


def setup(
    app: FastAPI,
    user_settings: Optional[AppSettings | CorsSettings | PostgresSettings] = None,
    db: Optional[Database] = None,
) -> None:

    # General
    if user_settings and isinstance(user_settings, AppSettings):

        app.title = user_settings.PROJECT_NAME

    # Exception handling
    app.add_exception_handler(errors.Error, exception_handler)

    # Database
    if user_settings:
        if not db and isinstance(user_settings, PostgresSettings):
            postgres_url: Optional[PostgresDsn] = user_settings.POSTGRES_URI

            if postgres_url:
                metadata = SETTINGS.sql.metadata or MetaData()
                db = databases.Database(postgres_url)

                configure({"sql": {"metadata": metadata, "database": db}}, partial=True)

    if db:
        init_db(app, db)

        async def on_startup() -> None:

            await start_database(app)

        async def on_shutdown() -> None:

            await stop_database(app)

        app.add_event_handler("startup", on_startup)
        app.add_event_handler("shutdown", on_shutdown)

    # Middleware
    if user_settings:

        if isinstance(user_settings, CorsSettings):

            app.add_middleware(
                CORSMiddleware,
                allow_origins=[
                    str(origin) for origin in user_settings.BACKEND_CORS_ORIGINS
                ],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
