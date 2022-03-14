from databases import Database
from fastapi import FastAPI
import pytest
from saas_toolkit.fastapi.database import init_db, start_database, stop_database


def test_init_db(app: FastAPI, db: Database):

    with pytest.raises(AttributeError):
        app.state.database

    init_db(app, db)

    assert app.state.database == db, "Database not added to app"


async def test_start_database(app: FastAPI, db: Database):

    init_db(app, db)

    await start_database(app)

    assert db.is_connected == True, "Database not connected"


async def test_stop_database(app: FastAPI, db: Database):

    init_db(app, db)

    await start_database(app)

    await stop_database(app)

    assert db.is_connected == False, "Database is still connected"
