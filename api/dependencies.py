"""The dependencies for the application"""
from typing import Union

from fastapi import Depends, Security, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status
from starlette.requests import Request

from api.utils import OAuth2PasswordBearerCookie, extract_result
from services import auth
from services.auth import is_valid_api_key
from services.auth.models import UserDTO

api_key_header = APIKeyHeader(name="x-api-key")
oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="api/login")


async def get_api_key_or_current_user(
    request: Request,
    header_key: str = Security(api_key_header),
    token: str = Depends(oauth2_scheme),
) -> Union[str, UserDTO]:
    """Dependency for retrieving and validating the API key from the header or cookie"""
    if header_key and await is_valid_api_key(request.state.auth_service, header_key):
        return header_key
    elif token:
        return await get_current_user(request, token)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="could not validate credentials"
    )


async def get_current_user(
    request: Request, token: str = Depends(oauth2_scheme)
) -> UserDTO:
    """Gets the current logged in user

    Args:
        request: the FastAPI request
        token: the JWT token got from the oauth headers

    Returns:
        the User who is logged in

    Raises:
        raises HTTPException in case of any error
    """
    resp = await auth.get_current_user(request.state.auth_service, token=token)
    return extract_result(resp)
