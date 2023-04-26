"""Routes that are public"""
from typing import List, Union

from fastapi import Query, Security, FastAPI
from fastapi.requests import Request
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.authentication import requires
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware

from api.auth import APIKeyHeaderAuthBackend
from api.models import SongDetail
from api.utils import extract_result
from services import auth, hymns
from services.auth.models import Application
from services.hymns.models import PaginatedResponse

public_api = FastAPI(root_path="/api")
public_api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
public_api.add_middleware(SlowAPIMiddleware)
public_api.add_middleware(
    AuthenticationMiddleware, backend=APIKeyHeaderAuthBackend(name="x-api-key")
)
public_api.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@public_api.post("/register", response_model=Application)
async def register_app(request: Request):
    """API route that registers a new app to get a new API key.

    It returns the application with the raw key but saves a hashed key in the auth service
    such that an API key is seen only once
    """
    res = await auth.register_app(request.app.state.auth_service)
    return extract_result(res)


@requires("authenticated")
@public_api.get("/{language}/{number}", response_model=SongDetail)
async def get_song_detail(
    request: Request,
    language: str,
    number: int,
    translation: List[str] = Query(default=()),
):
    """Displays the details of the song whose number is given"""
    languages = [language, *translation]
    song = SongDetail(number=number, translations={})

    for lang in languages:
        res = await hymns.get_song_by_number(
            request.app.state.hymns_service, number=number, language=lang
        )
        _translation = extract_result(res)
        song.translations[lang] = _translation

    return song


@requires("authenticated")
@public_api.get("/{language}/find-by-title/{q}", response_model=PaginatedResponse)
async def query_by_title(
    request: Request,
    language: str,
    q: str,
    skip: int = 0,
    limit: int = 0,
):
    """Returns list of songs whose titles match the search term `q`"""
    res = await hymns.query_songs_by_title(
        request.app.state.hymns_service, q=q, language=language, skip=skip, limit=limit
    )
    return extract_result(res)


@requires("authenticated")
@public_api.get("/{language}/find-by-number/{q}", response_model=PaginatedResponse)
async def query_by_number(
    request: Request,
    language: str,
    q: int,
    skip: int = 0,
    limit: int = 0,
):
    """Returns list of songs whose numbers match the search term `q`"""
    res = await hymns.query_songs_by_number(
        request.app.state.hymns_service, q=q, language=language, skip=skip, limit=limit
    )
    return extract_result(res)
