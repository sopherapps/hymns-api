"""Common state of the admin app"""
from typing import Optional, List

import funml as ml
from fastapi import FastAPI, Depends
from starlette.requests import Request
from starlette.templating import Jinja2Templates

import settings
from api.errors import HTTPAuthenticationError
from api.security import OAuth2BearerScheme
from api.utils import raise_http_error
from services import auth
from services.auth.models import UserDTO

admin_site = FastAPI(root_path="/admin")
cookie_ttl: int = 1800
templates = Jinja2Templates(directory=settings.get_templates_folder())
oauth2_scheme = OAuth2BearerScheme(token_url="/admin/login")


async def get_current_user(
    request: Request,
    tokens: Optional[List[str]] = Depends(oauth2_scheme.get_multiple_tokens),
) -> UserDTO:
    """Gets the current logged in user

    If the user is not logged in, it redirects to the login page

    Args:
        request: the FastAPI request
        tokens: the list of potential JWT tokens got from the oauth headers, cookies etc

    Returns:
        the User who is logged in
    """
    if len(tokens) < 1:
        raise HTTPAuthenticationError()

    exp = None
    for token in tokens:
        resp = await auth.get_current_user(request.app.state.auth_service, token=token)
        if ml.is_ok(resp):
            return resp.value
        else:
            exp = resp.value

    raise_http_error(exp)
