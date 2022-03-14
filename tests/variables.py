import databases
from fastapi import FastAPI
import sqlalchemy


DATABASE_URL = "sqlite:///db.sqlite"
DATABASE = databases.Database(DATABASE_URL)
METADATA = sqlalchemy.MetaData()
