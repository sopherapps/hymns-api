"""A collection of error types for this service"""


class ValidationError(Exception):
    """Exception returned when data is not of expected type or shape.

    Args:
        msg: the msg
    """

    def __init__(self, msg: str = ""):
        self.msg = msg

    def __repr__(self):
        return f"ValidationError: {self.msg}"

    def __str__(self):
        return self.__repr__()
