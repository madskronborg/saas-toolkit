from fastapi import Response
from .. import domain


class NoOpTransport(domain.ITransport[None, None]):
    async def get_login_response(self, token: str, response: Response) -> None:
        return None

    async def get_logout_response(self, token: str, response: Response) -> None:
        return None
