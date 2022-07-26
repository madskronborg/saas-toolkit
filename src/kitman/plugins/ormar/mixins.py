import asyncio
from typing import Type

from sqlalchemy import desc
from .models import ormar, QuerysetProxy
from typing_extensions import Self


class OrderableMixin:
    class MetaOptions:

        orders_by = ["order"]

    order: int = ormar.SmallInteger(default=1)


class TreeMixin:

    parent: Self | None
    children: list[Self] | QuerysetProxy[Self]

    def __new__(cls: type[Self], *args, **kwargs) -> Self:

        klass = super().__new__(cls, *args, **kwargs)

        klass.build_parent_field()

        return klass

    @classmethod
    def build_parent_field(cls) -> None:
        cls.parent = ormar.ForeignKey(cls, nullable=True, related_name="children")

    async def get_descendants(self) -> list[Self]:

        descendants: list[Self] = [self]

        children: list[Self] = self.children

        tasks = []

        for child in children:

            tasks.append(child.get_descendants())

        results: list[list[Self]] = await asyncio.gather(*tasks)

        for result in results:
            descendants.extend(result)

        return descendants

    async def get_ascendants(self) -> list[Self]:

        ascendants: list[Self] = []

        subject: Self | None = self

        while subject is not None:

            ascendants.append(self)

            if subject.parent:
                await subject.parent.load()

                subject = subject.parent

        return ascendants.reverse()

    async def get_tree(self) -> list[Self]:

        tree: list[Self] = []

        tasks: list[list[Self]] = [self.get_ascendants(), self.get_descendants()]

        results = await asyncio.gather(*tasks)

        for result in results:
            tree.extend(result)

        return tree
