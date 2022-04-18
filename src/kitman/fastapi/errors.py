from fastapi import Request
from fastapi.responses import JSONResponse
from kitman import errors


async def exception_handler(request: Request, exc: errors.Error) -> JSONResponse:

    data = dict(
        status_code=exc.status_code,
    )

    content: dict = dict(detail=exc.message, code=exc.code)

    data["content"] = content

    return JSONResponse(**data)
