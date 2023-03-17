"""A collection of error types for all services"""


class NotFoundError(Exception):
    """Exception returned when data is not found.

    Args:
        arg: the argument which was not found
    """

    def __init__(self, arg: str = ""):
        self.arg = arg

    def __repr__(self):
        return f"NotFoundError: Not found {self.arg}"
