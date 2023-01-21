from typing import TypeVar
from beanie import Document
from beanie.odm.interfaces.find import FindMany


TDocument = TypeVar("TDocument", bound=Document)
