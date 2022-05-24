from kitman.core import sdk
from kitman.core.sdk import action


class BaseService(sdk.BaseClient):
    pass


class BaseHTTPService(sdk.AsyncHTTPClient):
    pass


class BaseServiceExtension(sdk.AsyncClientExtension):
    pass
