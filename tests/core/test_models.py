import datetime
from uuid import UUID
from databases import Database
from fastapi import FastAPI
from ormar import pre_update
from saas_toolkit.fastapi.database import start_database

from saas_toolkit.core import models


class MyModel(models.BaseModel):
    class Meta(models.BaseMeta):
        pass


async def test_models(app: FastAPI, db: Database):

    instance = await MyModel.objects.create()

    assert str(instance) == f"{instance.__class__.__name__} with ID: {instance.id}"

    assert isinstance(instance.id, UUID), "Model id is not a uuid4"

    assert isinstance(
        instance.created, datetime.datetime
    ), "Model created is not a datetime"
    assert isinstance(
        instance.updated, datetime.datetime
    ), "Model updated is not a datetime"

    # Test updated changes when updated instance
    pre_updated = instance.updated
    await instance.update()

    assert instance.updated != pre_updated, "Model updated field is not updated"
