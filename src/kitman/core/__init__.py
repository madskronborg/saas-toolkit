from kitman.conf import settings
from kitman import errors

from . import errors

if not settings:
    raise errors.ConfigurationError("Settings have not been configured")

# Exports
# from . import converters, models, schemas
