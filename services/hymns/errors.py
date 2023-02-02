"""A collection of error types for this service"""


class NotFoundError(BaseException):
    """Exception returned when data is not found.

    Args:
        arg: the argument which was not found
    """

    def __init__(self, arg: str = ""):
        self.arg = arg

    def __repr__(self):
        return f"NotFoundError: Not found {self.arg}"


class ValidationError(BaseException):
    """Exception returned when data is not of expected type or shape.

    Args:
        msg: the msg
    """

    def __init__(self, msg: str = ""):
        self.msg = msg

    def __repr__(self):
        return f"ValidationError: {self.msg}"
