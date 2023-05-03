"""Common state of the admin app"""
import typing

import itsdangerous
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from starlette.datastructures import Secret
from starlette.middleware.sessions import SessionMiddleware
from starlette.types import ASGIApp, Scope, Receive, Send

import settings
from api.errors import HTTPAuthenticationError
from api.security import OAuth2BearerScheme
from services.auth.models import UserDTO

admin_site = FastAPI(root_path="/admin")
cookie_ttl: int = 1800
templates = Jinja2Templates(directory=settings.get_templates_folder())
oauth2_scheme = OAuth2BearerScheme(token_url="/admin/login")


class LazySessionMiddleware(SessionMiddleware):
    """Session middleware that loads any missing props from settings in case they were not supplied on initialization"""

    def __init__(
        self,
        app: ASGIApp,
        secret_key: typing.Optional[typing.Union[str, Secret]] = None,
        session_cookie: str = "session",
        max_age: typing.Optional[int] = 14 * 24 * 60 * 60,
        path: str = "/",
        same_site: typing.Literal["lax", "strict", "none"] = "lax",
        https_only: typing.Optional[bool] = None,
    ):
        self.__secret_key = secret_key
        self.__https_only = https_only

        _secret_key = "" if secret_key is None else secret_key
        _https_only = False if https_only is None else https_only
        super().__init__(
            app, _secret_key, session_cookie, max_age, path, same_site, _https_only
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self.__secret_key is None:
            self.__secret_key = settings.get_api_secret()
            self.signer = itsdangerous.TimestampSigner(str(self.__secret_key))

        if self.__https_only is None:
            self.__https_only = settings.is_production()
            if self.__https_only:  # Secure flag can be used with HTTPS only
                self.security_flags += "; secure"

        return await super().__call__(scope, receive, send)


async def get_current_user(
    request: Request,
    # tokens: Optional[List[str]] = Depends(oauth2_scheme.get_multiple_tokens),
) -> UserDTO:
    """Gets the current logged in user

    If the user is not logged in, it redirects to the login page

    Args:
        request: the FastAPI request
        # tokens: the list of potential JWT tokens got from the oauth headers, cookies etc

    Returns:
        the User who is logged in
    """
    user = request.session.get("user", None)
    if user is None:
        raise HTTPAuthenticationError()
    return user
