from fastapi import FastAPI
from databases import Database
from kitman.logging import logger


def init_db(app: FastAPI, db: Database) -> None:
    """
    init_db Add `database` to `app.state`

    Args:
        app (FastAPI): A FastAPI instance
        db (Database): A databases.Database instance
    """

    app.state.database = db


async def start_database(app: FastAPI) -> None:

    logger.info("Starting database..")
    database_: Database = app.state.database
    if not database_.is_connected:
        await database_.connect()

    logger.success("Database started!")


async def stop_database(app: FastAPI) -> None:

    logger.info("Shutting down database..")
    database_: Database = app.state.database
    if database_.is_connected:
        await database_.disconnect()

    logger.success("Shutdown complete!")
