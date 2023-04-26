from typing import List, Optional

import funml as ml
from fastapi.openapi.models import OAuthFlows
from fastapi.security import OAuth2, APIKeyHeader
from fastapi.security.utils import get_authorization_scheme_param
from starlette.authentication import (
    AuthenticationBackend,
    AuthenticationError,
    AuthCredentials,
    SimpleUser,
)
from starlette.requests import Request

import services
from api.errors import HTTPAuthenticationError
from services.auth.models import UserDTO


# async def get_api_key(
#     request: Request,
#     header_key: str = Security(api_key_header),
# ) -> Union[str, UserDTO]:
#     """Dependency for retrieving and validating the API key from the header or cookie"""
#     if header_key and await is_valid_api_key(
#         request.app.state.auth_service, header_key
#     ):
#         return header_key
#
#     raise HTTPException(
#         status_code=status.HTTP_403_FORBIDDEN, detail="could not validate credentials"
#     )


# async def get_current_user(
#     request: Request,
#     tokens: Optional[List[str]] = Depends(oauth2_scheme.get_multiple_tokens),
# ) -> UserDTO:
#     """Gets the current logged in user
#
#     If the user is not logged in, it redirects to the login page
#
#     Args:
#         request: the FastAPI request
#         tokens: the list of potential JWT tokens got from the oauth headers, cookies etc
#
#     Returns:
#         the User who is logged in
#     """
#     if len(tokens) < 1:
#         raise HTTPAuthenticationError()
#
#     exp = None
#     for token in tokens:
#         resp = await auth.get_current_user(request.app.state.auth_service, token=token)
#         if ml.is_ok(resp):
#             return resp.value
#         else:
#             exp = resp.value
#
#     raise_http_error(exp)


class OAuth2BearerScheme(OAuth2):
    def __init__(
        self,
        token_url: str,
        scheme_name: str = "bearer",
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlows(password={"tokenUrl": token_url, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def get_multiple_tokens(self, request: Request) -> List[str]:
        """Retrieves the tokens from the header, cookie etc as a list"""
        tokens = []
        possible_locations = ["headers", "cookies"]

        for location in possible_locations:
            auth = getattr(request, location).get("Authorization")
            if auth:
                scheme, param = get_authorization_scheme_param(auth)
                if scheme.lower() == self.scheme_name:
                    tokens.append(param)

        return tokens

    async def __call__(self, request: Request) -> Optional[str]:
        tokens = await self.get_multiple_tokens(request)
        if len(tokens) < 1:
            if self.auto_error:
                raise HTTPAuthenticationError()
            else:
                return None

        return tokens[0]


class APIKeyHeaderScheme(APIKeyHeader):
    def __init__(
        self,
        *,
        name: str,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        auto_error: bool = True
    ):
        super().__init__(
            name=name,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    def get_api_key(self, request: Request):
        """Gets the API key passed in the header"""
        return request.headers.get(self.model.name)


class BearerTokenAuthBackend(AuthenticationBackend):
    """An auth backend for bearer-token-header-or-cookie-driven authentication"""

    def __init__(
        self,
        login_url: str,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):
        self.scheme = OAuth2BearerScheme(
            token_url=login_url,
            scheme_name=scheme_name,
            scopes=scopes,
            auto_error=auto_error,
        )
        self.__scopes = list(scopes.keys()) if isinstance(scopes, dict) else []

    async def authenticate(self, request: Request):
        tokens = await self.scheme.get_multiple_tokens(request)
        if len(tokens) < 1:
            return

        exp: Optional[Exception] = None
        user: Optional[UserDTO] = None
        for token in tokens:
            resp = await services.auth.get_current_user(
                request.app.state.auth_service, token=token
            )
            if ml.is_ok(resp):
                user = resp.value
            else:
                exp = resp.value

        if user is None:
            raise AuthenticationError(exp)

        return AuthCredentials(scopes=self.__scopes), SimpleUser(username=user.username)


class APIKeyHeaderAuthBackend(AuthenticationBackend):
    """An auth backend for API-key-header-driven auth"""

    def __init__(
        self,
        *,
        name: str,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
        scopes: Optional[dict] = None
    ):
        self.scheme = APIKeyHeaderScheme(
            name=name,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )
        self.__scopes = list(scopes.keys()) if isinstance(scopes, dict) else []

    async def authenticate(self, request: Request):
        api_key = self.scheme.get_api_key(request)
        if not api_key:
            raise AuthenticationError("API key not set")

        if await services.auth.is_valid_api_key(
            request.app.state.auth_service, api_key
        ):
            return AuthCredentials(scopes=self.__scopes), SimpleUser(
                username="anonymous"
            )
        raise AuthenticationError("could not validate credentials")
