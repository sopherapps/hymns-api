"""Routes for the admin site"""
import http.cookies
from typing import List

from fastapi import Depends, Form, FastAPI, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from starlette.datastructures import MutableHeaders

import settings
from api.dependencies import get_current_user, oauth2_scheme
from api.models import PartialSong
from api.utils import extract_result, CSRFMiddleware
from services import hymns, auth
from services.auth.models import UserDTO, LoginResponse, OTPResponse
from services.hymns.models import Song

admin_site = FastAPI(openapi_prefix="/admin")
admin_site.add_middleware(CSRFMiddleware)
admin_site.mount(
    "/static", StaticFiles(directory=settings.get_static_folder()), name="static"
)
_cookie_ttl: int = 1800
templates = Jinja2Templates(directory="templates")


@admin_site.put("/{language}/{number}", response_model=Song)
async def update_song(
    request: Request,
    language: str,
    number: int,
    song: PartialSong,
    user: UserDTO = Depends(get_current_user),
):
    """Updates the song whose number is given"""
    original = await _get_song(request, language=language, number=number)
    new_data = {**original.dict(), **song.dict(exclude_unset=True)}
    new_song = Song(**new_data)
    res = await hymns.add_song(request.app.state.hymns_service, song=new_song)
    return extract_result(res)


@admin_site.delete("/{language}/{number}", response_model=List[Song])
async def delete_song(
    request: Request,
    language: str,
    number: int,
    user: UserDTO = Depends(get_current_user),
):
    """Deletes the song whose number is given"""
    res = await hymns.delete_song(
        request.app.state.hymns_service, number=number, language=language
    )
    return extract_result(res)


@admin_site.post("/", response_class=HTMLResponse)
async def create_song(
    request: Request, song: Song, user: UserDTO = Depends(get_current_user)
):
    """API route that creates a new song"""
    res = await hymns.add_song(request.app.state.hymns_service, song=song)
    new_song = extract_result(res)
    response = RedirectResponse(
        url=request.url_for(
            "get_edit_song", language=new_song.language, number=new_song.number
        )
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
    # FIXME: However this makes it impossible to set the cookie
    # FIXME: The status code is also not working as expected. Could it be due to overriding the BaseHTTPMiddleware?
    response = RedirectResponse(url=verify_otp_url, status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        "Authorization",
        value=f"{login_result.token_type} {login_result.access_token}",
        domain=verify_otp_url.hostname,
        httponly=True,
        max_age=_cookie_ttl,
        expires=_cookie_ttl,
        secure=verify_otp_url.is_secure,
    )
    return response


@admin_site.post("/verify-otp", response_class=HTMLResponse)
async def verify_otp(
    request: Request, otp: str = Form(), token: str = Depends(oauth2_scheme)
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
        max_age=_cookie_ttl,
        expires=_cookie_ttl,
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


@admin_site.get("/create", response_class=HTMLResponse)
async def get_create_song(request: Request, user: UserDTO = Depends(get_current_user)):
    """Creates a new song"""
    return templates.TemplateResponse("create.html", {"request": request})


@admin_site.get("/edit/{language}/{number}", response_class=HTMLResponse)
async def get_edit_song(
    request: Request,
    language: str,
    number: int,
    user: UserDTO = Depends(get_current_user),
):
    """Edits a new song"""
    song = await _get_song(request, language=language, number=number)
    return templates.TemplateResponse("edit.html", {"request": request, "song": song})


@admin_site.get("/", response_class=HTMLResponse)
async def get_admin_home(request: Request, user: UserDTO = Depends(get_current_user)):
    """Admin home"""
    return templates.TemplateResponse("index.html", {"request": request})


async def _get_song(request: Request, language: str, number: int) -> Song:
    """Gets the song for the given language and song number"""
    res = await hymns.get_song_by_number(
        request.app.state.hymns_service, number=number, language=language
    )
    return extract_result(res)
