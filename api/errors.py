"""Exceptions for the api service"""
from typing import Any, Optional, Dict, Tuple

from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED


class HTTPAuthenticationError(HTTPException):
    """Exception returned when authentication fails.

    Args:
        status_code: the HTTP status code
        detail: the detail to pass to the client if necessary
        headers: the headers to pass to the client
    """

    def __init__(
        self,
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class HTTPExceptionWithLink(HTTPException):
    """General HTTPException that has a helpful link

    Args:
        status_code: the HTTP status code
        detail: the detail to pass to the client if necessary
        headers: the headers to pass to the client
        helpful_link: the link and anchor tuple to help one rectify the problem
    """

    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
        helpful_link: Optional[Tuple[str, str]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.helpful_link = helpful_link
