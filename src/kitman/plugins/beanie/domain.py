from typing import TypeVar

from beanie import Document
from beanie.odm.queries.find import FindMany

TDocument = TypeVar("TDocument", bound=Document)
