from kitman import errors


class InvalidParams(errors.HTTPError):
    pass


class InvalidData(errors.HTTPError):
    pass
