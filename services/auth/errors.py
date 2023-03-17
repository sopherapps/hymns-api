"""A collection of error types for this service"""


class AuthenticationError(Exception):
    """Exception returned when authentication fails.

    Args:
        msg: the msg
    """

    def __init__(self, msg: str = ""):
        self.msg = msg

    def __repr__(self):
        return f"AuthenticationError: {self.msg}"
