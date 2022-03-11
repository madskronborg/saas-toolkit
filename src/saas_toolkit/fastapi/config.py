from typing import Any, Optional
import databases
from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator
from typing import Optional
from .database import init_db, start_database, stop_database
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from databases import Database
from saas_toolkit import errors
from sqlalchemy import MetaData
from saas_toolkit.config import configure, settings
from fastapi.middleware.cors import CORSMiddleware


class AppSettings(BaseSettings):

    PROJECT_NAME: str
    ENV: str = "development"
    SECRET: str = "JDEkd3FLMERidi4kelpuQ2tWelFsM3NuVUdiZXFGUjltMQo="

    class Config:
        case_sensitive = True


class CorsSettings(BaseSettings):

    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]

        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


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


async def exception_handler(request: Request, exc: errors.Error) -> JSONResponse:

    data = dict(
        status_code=exc.status_code,
    )

    content: dict = dict(detail=exc.message, code=exc.code)

    data["content"] = content

    return JSONResponse(**data)


def setup(
    app: FastAPI, settings: Optional[BaseSettings] = None, db: Optional[Database] = None
) -> None:

    # General
    if settings and isinstance(settings, AppSettings):

        if not app.title:
            app.title = settings.PROJECT_NAME

    # Exception handling
    app.add_exception_handler(errors.Error, exception_handler)

    # Database
    if settings:
        if not db and isinstance(settings, PostgresSettings):
            postgres_url: Optional[PostgresDsn] = settings.POSTGRES_URI

            if postgres_url:
                metadata = MetaData()
                db = databases.Database(postgres_url)

                configure({"database": {"metadata": metadata}})

    if db:
        init_db(app, db)

        async def on_startup() -> None:

            await start_database(app)

        async def on_shutdown() -> None:

            await stop_database(app)

        app.add_event_handler("startup", on_startup)
        app.add_event_handler("shutdown", on_shutdown)

    # Middleware
    if settings:

        if isinstance(settings, CorsSettings):

            app.add_middleware(
                CORSMiddleware,
                allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
