from kitman.conf import SETTINGS
from kitman import errors

from . import errors

if not SETTINGS:
    raise errors.ConfigurationError("Settings have not been configured")

# Exports
# from . import converters, models, schemas
