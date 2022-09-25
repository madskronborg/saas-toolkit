from kitman.core import exceptions


class NoNamespaceError(exceptions.ConfigurationError):

    pass


class StrategyDestroyNotSupportedError(Exception):
    pass


class TransportLogoutNotSupportedError(Exception):
    pass


class DuplicateBackendNamesError(Exception):
    pass
