from typing import Optional
from pydantic import BaseModel


class Error(Exception):

    message: str | int | dict | list
    code: Optional[int] = None
    status_code: int

    def __init__(
        self,
        message: str | int | dict | list,
        code: Optional[int] = None,
        status_code: int = 400,
    ) -> None:
        super().__init__(message)

        self.message = message
        self.code = code
        self.status_code = status_code


class ConfigurationError(Error):
    pass
