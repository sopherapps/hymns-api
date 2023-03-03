from typing import Any, Callable, TypeVar

import funml as ml
from fastapi import HTTPException, status

from services import hymns


T = TypeVar("T")


def try_to(do: Callable[[Any], T]) -> Callable[[ml.Result], T]:
    """Creates a function that calls `do` if the result is ml.Result.OK or raises an HTTP exception if result.ERR.

    Args:
        do: the callable to call on the funml.Result.OK

    Returns:
        a new function that can work on a funml.Result value
    """
    return (
        ml.match()
        .case(ml.Result.OK(Any), do)
        .case(ml.Result.ERR(Exception), do=_raise_http_error)
    )


def _raise_http_error(exp: Exception):
    """Raises an HTTP exception given exp.

    Args:
        exp: the Exception passed to it

    Raises:
        HTTPException: the `exp` with an appropriate status code
    """
    code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if isinstance(exp, hymns.errors.NotFoundError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exp, hymns.errors.ValidationError):
        code = status.HTTP_400_BAD_REQUEST

    raise HTTPException(status_code=code, detail=f"{exp}")
