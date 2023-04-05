from typing import Any, Callable, TypeVar

import funml as ml
from fastapi import HTTPException, status

import services


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
        .case(ml.Result.ERR(Exception), do=raise_http_error)
        .case(Any, do=lambda v: v)
    )


def raise_http_error(exp: Exception):
    """Raises an HTTP exception given exp.

    Args:
        exp: the Exception passed to it

    Raises:
        HTTPException: the `exp` with an appropriate status code
    """
    code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if isinstance(exp, services.errors.NotFoundError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exp, services.hymns.errors.ValidationError):
        code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exp, services.auth.errors.AuthenticationError):
        code = status.HTTP_403_FORBIDDEN

    raise HTTPException(status_code=code, detail=f"{exp}")
