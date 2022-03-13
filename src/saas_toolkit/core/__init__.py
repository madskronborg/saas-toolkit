from saas_toolkit.conf import SETTINGS
from saas_toolkit import errors

from . import errors

if not SETTINGS:
    raise errors.ConfigurationError("Settings have not been configured")
