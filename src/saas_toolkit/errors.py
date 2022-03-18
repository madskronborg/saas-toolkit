from typing import Optional
from pydantic import BaseModel


class Error(Exception):

    message: str | int | dict | list
    code: Optional[int] = None
    status_code: int = 400

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


class ConfigurationError(Error):
    pass


class NotFound(Error):
    """
    NotFound.

    Raises a HTTP 404 not found error.
    """

    status_code: int = 404
