"""The RESTful API and the admin site
"""
import gc
from typing import Optional, List

from fastapi import FastAPI, Query, Security, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.api_key import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from slowapi.middleware import SlowAPIMiddleware


import settings
from api.models import (
    Song,
    SongDetail,
    PartialSong,
    OTPRequest,
)
from api.utils import try_to
from services import hymns, config, auth

from services.auth import is_valid_api_key

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from services.auth.models import (
    UserDTO,
    LoginResponse,
    OTPResponse,
    ChangePasswordRequest,
    Application,
)
from services.hymns.models import PaginatedResponse
from services.store import Store

api_key_header = APIKeyHeader(name="x-api-key")

hymns_service: Optional[hymns.types.HymnsService] = None
auth_service: Optional[auth.types.AuthService] = None
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# app set up
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def _get_api_key(header_key: str = Security(api_key_header)):
    """Dependency for retrieving and validating the API key from the header or cookie"""
    if await is_valid_api_key(auth_service, header_key):
        return header_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="could not validate credentials"
    )


async def _get_current_user(token: str = Depends(oauth2_scheme)) -> UserDTO:
    """Gets the current logged in user

    Args:
        token: the JWT token got from the oauth headers

    Returns:
        the User who is logged in

    Raises:
        raises HTTPException in case of any error
    """
    resp = await auth.get_current_user(auth_service, token=token)
    convert_to_user = try_to(lambda v: v)
    return convert_to_user(resp)


@app.on_event("startup")
async def start():
    """Initializes the hymns service"""
    settings.initialize()

    hymns_db_uri = settings.get_hymns_db_uri()
    auth_db_uri = settings.get_auth_db_uri()
    config_db_uri = settings.get_config_db_uri()
    hymns_service_conf = settings.get_hymns_service_config()
    api_key_length = settings.get_api_key_length()
    api_secret = settings.get_api_secret()
    jwt_ttl = settings.get_jwt_ttl_in_sec()
    max_login_attempts = settings.get_max_login_attempts()
    mail_config = settings.get_email_config()
    mail_sender = settings.get_auth_email_sender()
    otp_verification_url = settings.get_otp_verification_url()

    await config.save_service_config(config_db_uri, hymns_service_conf)

    global app

    # hymns service
    global hymns_service
    hymns_service = await hymns.initialize(hymns_db_uri)

    # auth service
    global auth_service
    auth_service = await auth.initialize(
        uri=auth_db_uri,
        key_size=api_key_length,
        api_secret=api_secret,
        jwt_ttl=jwt_ttl,
        max_login_attempts=max_login_attempts,
        mail_config=mail_config,
        mail_sender=mail_sender,
    )
    app.state.auth_service = auth_service
    app.state.otp_verification_url = otp_verification_url

    # API limiter
    app.state.limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[settings.get_rate_limit()],
        enabled=settings.get_is_rate_limit_enabled(),
    )


@app.on_event("shutdown")
async def shutdown():
    """Shuts down the application"""
    # Shut down all stores
    await Store.destroy_stores()
    gc.collect()


@app.post("/api/login", response_model=LoginResponse)
async def api_login(data: OAuth2PasswordRequestForm = Depends()):
    """API route that logins in admin users"""
    otp_url = app.state.otp_verification_url
    res = await auth.login(
        auth_service,
        username=data.username,
        password=data.password,
        otp_verification_url=otp_url,
    )

    transform = try_to(lambda v: v)
    return transform(res)


@app.post("/api/verify-otp", response_model=OTPResponse)
async def api_verify_otp(data: OTPRequest, token: str = Depends(oauth2_scheme)):
    """Verifies the one-time password got by email"""
    res = await auth.verify_otp(auth_service, otp=data.otp, unverified_token=token)
    transform = try_to(lambda v: v)
    return transform(res)


@app.post("/api/change-password")
async def api_change_password(data: ChangePasswordRequest):
    """Initializes the password change process"""
    res = await auth.change_password(auth_service, data=data)
    transform = try_to(lambda v: v)
    return transform(res)


@app.post("/api/register", response_model=Application)
async def api_register_app():
    """API route that registers a new app to get a new API key.

    It returns the application with the raw key but saves a hashed key in the auth service
    such that an API key is seen only once
    """
    res = await auth.register_app(auth_service)
    transform = try_to(lambda v: v)
    return transform(res)


@app.get("/api/{language}/{number}", response_model=SongDetail)
async def api_get_song_detail(
    language: str,
    number: int,
    translation: List[str] = Query(default=()),
    api_key: str = Security(_get_api_key),
):
    """Displays the details of the song whose number is given"""
    languages = [language, *translation]
    song = SongDetail(number=number, translations={})

    for lang in languages:
        _translation = await _get_song(language=lang, number=number)
        song.translations[lang] = _translation

    return song


@app.get("/api/{language}/find-by-title/{q}", response_model=PaginatedResponse)
async def api_query_by_title(
    language: str,
    q: str,
    skip: int = 0,
    limit: int = 0,
    api_key: str = Security(_get_api_key),
):
    """Returns list of songs whose titles match the search term `q`"""
    res = await hymns.query_songs_by_title(
        hymns_service, q=q, language=language, skip=skip, limit=limit
    )
    transform = try_to(lambda v: v)
    return transform(res)


@app.get("/api/{language}/find-by-number/{q}", response_model=PaginatedResponse)
async def api_query_by_number(
    language: str,
    q: int,
    skip: int = 0,
    limit: int = 0,
    api_key: str = Security(_get_api_key),
):
    """Returns list of songs whose numbers match the search term `q`"""
    res = await hymns.query_songs_by_number(
        hymns_service, q=q, language=language, skip=skip, limit=limit
    )
    transform = try_to(lambda v: v)
    return transform(res)


@app.put("/api/{language}/{number}", response_model=Song)
async def api_update_song(
    language: str,
    number: int,
    song: PartialSong,
    user: UserDTO = Depends(_get_current_user),
):
    """Updates the song whose number is given"""
    original = await _get_song(language=language, number=number)
    new_data = {**original.dict(), **song.dict(exclude_unset=True)}
    new_song = Song(**new_data)
    res = await hymns.add_song(hymns_service, song=new_song)
    transform = try_to(lambda v: v)
    return transform(res)


@app.delete("/api/{language}/{number}", response_model=List[Song])
async def api_delete_song(
    language: str, number: int, user: UserDTO = Depends(_get_current_user)
):
    """Deletes the song whose number is given"""
    res = await hymns.delete_song(hymns_service, number=number, language=language)
    transform = try_to(lambda v: v)
    return transform(res)


@app.post("/api", response_model=Song)
async def api_create_song(song: Song, user: UserDTO = Depends(_get_current_user)):
    """API route that creates a new song"""
    res = await hymns.add_song(hymns_service, song=song)
    transform = try_to(lambda v: v)
    return transform(res)


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    """HTML template route that logins in admin users"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/verify-otp", response_class=HTMLResponse)
async def verify_otp(request: Request):
    """HTML template route that verifies the one-time password got by email"""
    return templates.TemplateResponse("verify-otp.html", {"request": request})


@app.get("/change-password", response_class=HTMLResponse)
async def change_password(request: Request):
    """HTML template route that initializes the password change process"""
    return templates.TemplateResponse("change-password.html", {"request": request})


@app.get("/create", response_class=HTMLResponse)
async def create_song(request: Request, user: UserDTO = Depends(_get_current_user)):
    """Creates a new song"""
    return templates.TemplateResponse("create.html", {"request": request})


@app.get("/edit/{language}/{number}", response_class=HTMLResponse)
async def update_song(
    request: Request,
    language: str,
    number: int,
    user: UserDTO = Depends(_get_current_user),
):
    """Edits a new song"""
    song = await _get_song(language=language, number=number)
    return templates.TemplateResponse("edit.html", {"request": request, "song": song})


@app.get("/", response_class=HTMLResponse)
async def admin_home(request: Request, user: UserDTO = Depends(_get_current_user)):
    """Admin home"""
    return templates.TemplateResponse("index.html", {"request": request})


async def _get_song(language: str, number: int) -> Song:
    """Gets the song for the given language and song number"""
    res = await hymns.get_song_by_number(
        hymns_service, number=number, language=language
    )
    convert_to_song = try_to(lambda v: v)
    return convert_to_song(res)
