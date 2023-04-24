"""The dependencies for the application"""
from typing import Union, List, Optional

from fastapi import Depends, Security, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status
from starlette.requests import Request
import funml as ml
from starlette.status import HTTP_401_UNAUTHORIZED

from api.utils import OAuth2PasswordBearerCookie, extract_result, raise_http_error
from services import auth
from services.auth import is_valid_api_key
from services.auth.models import UserDTO

api_key_header = APIKeyHeader(name="x-api-key")
oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="admin/login")


async def get_api_key(
    request: Request,
    header_key: str = Security(api_key_header),
) -> Union[str, UserDTO]:
    """Dependency for retrieving and validating the API key from the header or cookie"""
    if header_key and await is_valid_api_key(
        request.app.state.auth_service, header_key
    ):
        return header_key

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="could not validate credentials"
    )


async def get_current_user(
    request: Request,
    tokens: Optional[List[str]] = Depends(oauth2_scheme.get_multiple_tokens),
) -> UserDTO:
    """Gets the current logged in user

    Args:
        request: the FastAPI request
        tokens: the list of potential JWT tokens got from the oauth headers, cookies etc

    Returns:
        the User who is logged in

    Raises:
        raises HTTPException in case of any error
    """
    if not tokens:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    exp = None
    for token in tokens:
        resp = await auth.get_current_user(request.app.state.auth_service, token=token)
        if ml.is_ok(resp):
            return resp.value
        else:
            exp = resp.value

    raise_http_error(exp)
