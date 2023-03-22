"""A collection of error types common to the whole app"""


class ConfigurationError(Exception):
    """Exception returned when configuration is botched.

    Args:
        msg: the msg
    """

    def __init__(self, msg: str = ""):
        self.msg = msg

    def __repr__(self):
        return f"ConfigurationError: {self.msg}"

    def __str__(self):
        return self.__repr__()
