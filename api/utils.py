from typing import Any, Optional, Tuple

import funml as ml
import starlette.authentication

from starlette import status

import services
from api.errors import HTTPExceptionWithLink


def extract_result(res: ml.Result) -> Any:
    """Returns the value in ml.Result.OK or raises an HTTP exception if res is result.ERR.

    Args:
        res: the result to extract

    Returns:
        the value in the ml.Result.OK

    Raises:
        HTTPException if res is an ml.Result.ERR
    """
    return (
        ml.match()
        .case(ml.Result.OK(Any), lambda v: v)
        .case(ml.Result.ERR(Exception), do=raise_http_error)
        .case(Any, do=lambda v: v)(res)
    )


def to_http_exception_with_link(exp: Exception) -> HTTPExceptionWithLink:
    """Converts any exception to an HTTPExceptionWithLink.

    Args:
        exp: the Exception passed to it

    Returns:
        HTTPExceptionWithLink: the `exp` with an appropriate status code
    """
    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    helpful_link: Optional[Tuple[str, str]] = None

    if isinstance(exp, services.errors.NotFoundError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exp, services.hymns.errors.ValidationError):
        code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exp, services.auth.errors.AuthenticationError):
        code = status.HTTP_403_FORBIDDEN
    elif isinstance(exp, services.auth.errors.OTPVerificationError):
        helpful_link = ("Otp verification", "get_verify_otp")
        code = status.HTTP_403_FORBIDDEN
    elif isinstance(exp, starlette.authentication.AuthenticationError):
        code = status.HTTP_403_FORBIDDEN

    return HTTPExceptionWithLink(
        status_code=code, detail=f"{exp}", helpful_link=helpful_link
    )


def raise_http_error(exp: Exception):
    """Raises an HTTP exception with a link given exp.

    Args:
        exp: the Exception passed to it

    Raises:
        HTTPExceptionWithLink: the `exp` with an appropriate status code
    """
    raise to_http_exception_with_link(exp)
