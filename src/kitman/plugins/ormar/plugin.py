from typing import Any
from databases import Database
from pydantic import BaseModel, PostgresDsn, validator
from sqlalchemy import MetaData
from kitman import Plugin, Kitman
from kitman.kitman import InstallableManager
from kitman.plugins.loguru import LoguruPlugin
from ormar import ModelMeta

from .models import BaseQueryset


class PostgresConf(BaseModel):

    SERVER: str | None = None
    USER: str | None
    PASSWORD: str
    DB: str
    URI: PostgresDsn | None = None

    @validator("URI", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgres",
            user=values.get("USER"),
            password=values.get("PASSWORD"),
            host=values.get("SERVER"),
            path=f"/{values.get('DB') or ''}",
        )


class OrmarConf(BaseModel):

    database: PostgresConf
    metadata: MetaData


class OrmarConnection(BaseModel):
    metadata: MetaData = MetaData()
    database: Database


class OrmarPluginManager(InstallableManager["OrmarPlugin", OrmarConf]):

    require_conf = True

    required_plugins = [
        (
            "logger",
            {
                LoguruPlugin,
            },
        )
    ]

    def install(self, kitman: Kitman, conf: OrmarConf | None = None) -> None:
        super().install(kitman, conf)

        if self.conf:
            db_url = self.conf.database.URI

            metadata = self.conf.metadata
            db = Database(db_url)

            self.parent.connection = OrmarConnection(metadata=metadata, database=db)

            self.parent.init_db()
            kitman.fastapi.add_event_handler("startup", self.parent.start_database)
            kitman.fastapi.add_event_handler("shutdown", self.parent.stop_database)


class OrmarPlugin(Plugin[OrmarConf]):
    name = "Ormar"
    description = "A kit for setting up Ormar with FastAPI"
    manager = OrmarPluginManager()
    connection: OrmarConnection

    # Helpers
    def get_model_meta_class(self) -> type[ModelMeta]:
        class BaseMeta(ModelMeta):
            metadata = self.connection.metadata
            database = self.connection.database
            queryset_class = BaseQueryset

        return BaseMeta

    # Deps
    def init_db(self):
        """
        init_db

        Add `database` to `app.state`
        """

        self.kitman.fastapi.state.db = self.connection.database

    async def start_database(self) -> None:

        logger_plugin: LoguruPlugin = self.manager.get_plugin("logger")
        logger = logger_plugin.get_logger()

        logger.info("Starting database..")
        database_: Database = self.kitman.fastapi.state.db
        if not database_.is_connected:
            await database_.connect()

        logger.success("Database started!")

    async def stop_database(self) -> None:

        logger_plugin: LoguruPlugin = self.manager.get_plugin("logger")
        logger = logger_plugin.get_logger()

        logger.info("Shutting down database..")
        database_: Database = self.kitman.fastapi.state.db
        if database_.is_connected:
            await database_.disconnect()

        logger.success("Shutdown complete!")
