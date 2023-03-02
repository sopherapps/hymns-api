from typing import Any

from fastapi import HTTPException, status

from services import hymns


def echo(v: Any):
    """Returns the input as is"""
    return v


def raise_http_error(exp: Exception):
    """Raises an HTTP exception given exp"""
    code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if isinstance(exp, hymns.errors.NotFoundError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exp, hymns.errors.ValidationError):
        code = status.HTTP_400_BAD_REQUEST

    raise HTTPException(status_code=code, detail=f"{exp}")
