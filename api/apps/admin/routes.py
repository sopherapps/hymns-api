"""Routes for the admin site"""
from typing import List

from fastapi import Depends, Form, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.authentication import requires
from starlette.middleware.authentication import AuthenticationMiddleware

import settings
from api.apps.admin.exc_handlers import (
    redirect_to_error_page,
    redirect_unauthenticated_to_login,
)
from api.apps.admin.state import admin_site, oauth2_backend, cookie_ttl, templates
from api.errors import HTTPAuthenticationError
from api.models import PartialSong
from api.utils import extract_result
from api.security import CSRFMiddleware
from services import hymns, auth
from services.auth.models import LoginResponse, OTPResponse
from services.hymns.models import Song

admin_site.add_middleware(SlowAPIMiddleware)
admin_site.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
admin_site.add_exception_handler(
    HTTPAuthenticationError, redirect_unauthenticated_to_login
)
admin_site.add_exception_handler(Exception, redirect_to_error_page)
admin_site.add_middleware(CSRFMiddleware)
admin_site.add_middleware(
    AuthenticationMiddleware, backend=oauth2_backend, on_error=redirect_to_error_page
)
admin_site.mount(
    "/static", StaticFiles(directory=settings.get_static_folder()), name="static"
)


@requires("authenticated")
@admin_site.put("/{language}/{number}", response_model=Song)
async def update_song(request: Request, language: str, number: int, song: PartialSong):
    """Updates the song whose number is given"""
    original = await _get_song(request, language=language, number=number)
    new_data = {**original.dict(), **song.dict(exclude_unset=True)}
    new_song = Song(**new_data)
    res = await hymns.add_song(request.app.state.hymns_service, song=new_song)
    return extract_result(res)


@requires("authenticated")
@admin_site.delete("/{language}/{number}", response_model=List[Song])
async def delete_song(request: Request, language: str, number: int):
    """Deletes the song whose number is given"""
    res = await hymns.delete_song(
        request.app.state.hymns_service, number=number, language=language
    )
    return extract_result(res)


@requires("authenticated")
@admin_site.post("/", response_class=HTMLResponse)
async def create_song(request: Request, song: Song):
    """API route that creates a new song"""
    res = await hymns.add_song(request.app.state.hymns_service, song=song)
    new_song = extract_result(res)
    response = RedirectResponse(
        url=request.url_for(
            "get_edit_song", language=new_song.language, number=new_song.number
        ),
        status_code=status.HTTP_302_FOUND,
    )
    return response


@admin_site.post("/login", response_class=RedirectResponse)
async def login(request: Request, data: OAuth2PasswordRequestForm = Depends()):
    """API route that logins in admin users"""
    verify_otp_url = request.url_for("get_verify_otp")
    res = await auth.login(
        request.app.state.auth_service,
        username=data.username,
        password=data.password,
        otp_verification_url=str(verify_otp_url),
    )
    login_result: LoginResponse = extract_result(res)
    # setting the status to 302 ensures the POST is transformed to a GET in the redirect
    # https://stackoverflow.com/questions/62119138/how-to-do-a-post-redirect-get-prg-in-fastapi
    response = RedirectResponse(url=verify_otp_url, status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        "Authorization",
        value=f"{login_result.token_type} {login_result.access_token}",
        domain=verify_otp_url.hostname,
        httponly=True,
        path="/",
        max_age=cookie_ttl,
        expires=cookie_ttl,
        secure=verify_otp_url.is_secure,
    )
    return response


@requires("authenticated")
@admin_site.post("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    """Logout the current user."""
    admin_home_url = request.url_for("get_admin_home")
    response = RedirectResponse(url=admin_home_url, status_code=status.HTTP_302_FOUND)
    # to delete the cookie, set it to a max age of 0 to discard the cookie immediately
    response.set_cookie(
        "Authorization",
        value="",
        domain=admin_home_url.hostname,
        httponly=True,
        path="/",
        max_age=0,
        expires=1,
        secure=admin_home_url.is_secure,
    )
    return response


@admin_site.post("/verify-otp", response_class=HTMLResponse)
async def verify_otp(
    request: Request, otp: str = Form(), token: str = Depends(oauth2_backend.scheme)
):
    """Verifies the one-time password got by email"""
    res = await auth.verify_otp(
        request.app.state.auth_service, otp=otp, unverified_token=token
    )
    otp_result: OTPResponse = extract_result(res)

    admin_home_url = request.url_for("get_admin_home")
    # setting the status to 302 ensures the POST is transformed to a GET in the redirect
    # https://stackoverflow.com/questions/62119138/how-to-do-a-post-redirect-get-prg-in-fastapi
    response = RedirectResponse(url=admin_home_url, status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        "Authorization",
        value=f"{otp_result.token_type} {otp_result.access_token}",
        domain=admin_home_url.hostname,
        httponly=True,
        path="/",
        max_age=cookie_ttl,
        expires=cookie_ttl,
        secure=admin_home_url.is_secure,
    )
    return response


@admin_site.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    """HTML template route that logins in admin users"""
    return templates.TemplateResponse("login.html", {"request": request})


@admin_site.get("/verify-otp", response_class=HTMLResponse)
async def get_verify_otp(request: Request):
    """HTML template route that verifies the one-time password got by email"""
    return templates.TemplateResponse("verify-otp.html", {"request": request})


@requires("authenticated")
@admin_site.get("/create", response_class=HTMLResponse)
async def get_create_song(request: Request):
    """Creates a new song"""
    return templates.TemplateResponse("create.html", {"request": request})


@requires("authenticated")
@admin_site.get("/edit/{language}/{number}", response_class=HTMLResponse)
async def get_edit_song(
    request: Request,
    language: str,
    number: int,
):
    """Edits a new song"""
    song = await _get_song(request, language=language, number=number)
    return templates.TemplateResponse("edit.html", {"request": request, "song": song})


@requires("authenticated")
@admin_site.get("/", response_class=HTMLResponse)
async def get_admin_home(request: Request):
    """Admin home"""
    return templates.TemplateResponse("index.html", {"request": request})


async def _get_song(request: Request, language: str, number: int) -> Song:
    """Gets the song for the given language and song number"""
    res = await hymns.get_song_by_number(
        request.app.state.hymns_service, number=number, language=language
    )
    return extract_result(res)
