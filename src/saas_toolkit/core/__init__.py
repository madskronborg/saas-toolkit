from saas_toolkit.config import settings
from saas_toolkit import errors

from . import errors

if not settings:
    raise errors.ConfigurationError("Settings have not been configured")
