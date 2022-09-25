from typing import Optional
from fastapi import status, exceptions


class HTTPError(Exception):

    message: str | int | dict | list
    code: Optional[int] = None
    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(
        self,
        message: str | int | dict | list,
        code: Optional[int] = None,
        status_code: Optional[int] = None,
    ) -> None:
        super().__init__(message)

        self.message = message

        if code:
            self.code = code

        if status_code:
            self.status_code = status_code


class ConfigurationError(HTTPError):
    pass


class NotFound(HTTPError):
    """
    NotFound.

    Raises a HTTP 404 not found error.
    """

    status_code: int = status.HTTP_404_NOT_FOUND
