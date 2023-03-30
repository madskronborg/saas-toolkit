import math
from typing import Awaitable, Callable, Generic, TypedDict

from beanie.operators import NotIn
from fastapi import Query

from .domain import FindMany, TDocument


class PaginatorResult(TypedDict, Generic[TDocument]):
    page: int
    size: int
    total: int
    items: list[dict]
    prev_page: int | None
    next_page: int | None


Paginator = Callable[
    [FindMany[TDocument], list[TDocument] | None, Callable[[TDocument], dict] | None],
    Awaitable[PaginatorResult[TDocument]],
]


def get_pagination(page: int = Query(1, ge=1), size: int = Query(100, le=100, ge=1)):
    async def paginate(
        query: FindMany[TDocument],
        extra_items: list[TDocument] | None = None,
        format_item: Callable[[TDocument], Awaitable[dict | TDocument]] | None = None,
    ) -> PaginatorResult[TDocument]:

        total = await query.count()
        total_pages = math.ceil(total / size)
        prev_page: int | None = None
        next_page: int | None = None

        # Query size can differ based on extra_items
        query_size = size - len(extra_items) if extra_items else size

        # Exclude extra_items from query - no need to fetch them twice
        if extra_items:
            query = query.find(
                NotIn(
                    query.document_model.uid,
                    [extra_item.uid for extra_item in extra_items],
                )
            )

        if page == 1:
            query = query.limit(query_size)
        else:
            skip = size * page
            query = query.skip(skip).limit(query_size)

        if page < total_pages:
            next_page = page + 1

        # Check if there is a previous page
        prev_page = None
        if page > 1:
            prev_page = page - 1

        items: list[dict] = [item.dict() for item in extra_items] if extra_items else []

        # print("Query size:", query_size, "page:", page, "Query Count:", await query.count())

        item: TDocument
        for item in await query.to_list():

            # print("Item is:", item)

            prepared_item = await format_item(item) if format_item else item.dict()

            if not isinstance(prepared_item, dict):
                prepared_item = prepared_item.dict()

            items.append(prepared_item)

        return {
            "page": page,
            "size": size,
            "total": total,
            "prev_page": prev_page,
            "next_page": next_page,
            "items": items,
        }

    return paginate
