from kitman import exceptions


class InvalidParams(exceptions.HTTPError):
    pass


class InvalidData(exceptions.HTTPError):
    pass
