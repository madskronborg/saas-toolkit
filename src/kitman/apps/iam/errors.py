from kitman.core import errors


class NoNamespaceError(errors.ConfigurationError):

    pass


class StrategyDestroyNotSupportedError(Exception):
    pass


class TransportLogoutNotSupportedError(Exception):
    pass


class DuplicateBackendNamesError(Exception):
    pass
