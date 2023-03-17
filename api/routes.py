"""
#### Details - GET `/{language}/{number}?translations={language}&translations={language}`...

Access: Public

Headers:

```python
{"X-API-KEY": "some api key"}
```

Params:

  - `language` = the language for the given hymn
  - `number` = the hymn number

Query Params:

  - `translations` = the list of other language translations to return for given song

Errors:

  - 404 - Not Found if language-number does not exist
  - 403 - Unauthorized if API key is not valid or was not supplied
  - 429 - Too many requests if user makes too many requests in a given amount of time

Response:

```python
class SongDetail(BaseModel):
    number: int
    translations: Dict[str, Song]
```

#### List - GET `/{language}/?page={int}&limit={int}&translations={language}&translations={language}`...

Access: Public

Headers:

```python
{"X-API-KEY": "some api key"}
```

Params:

  - `language` = the language for the given hymn
  - `number` = the hymn number

Query Params:

  - `page` (default = 1) - the page of results to return for the paginated format used
  - `limit` (default = 20) - the number of results per page to return for the paginated format used
  - `translations` = the list of other language translations to return for given song

Errors:

- 403 - Unauthorized if API Key is not valid or was not supplied
- 429 - Too many requests if user makes too many requests in a given amount of time

Response:

```python

SongTitle = str

class SongItem(BaseModel):
    number: int
    translations: Dict[Language, SongTitle]


class SongList(BaseModel):
    data: List[SongItem]
    page: int
    limit: int
```

#### Create - POST `/`

Access: Private Admin

Headers:

```python
{"Authorization": "Bearer some api key"}
```

Errors:

  - 409 - Conflict if language-number combination already exists
  - 403 - Unauthorized if authorization token is not valid or was not supplied
  - 400 - Bad Request if request passed is invalid
  - 429 - Too many requests if user makes too many requests in a given amount of time

Request:

```python
class CreateSongRequest(BaseModel):
    number: int
    language: Language
    title: str
    key: MusicalNote
    lines: List[List[LineSection]]
```

Response: `Song`

#### Update - PUT `/{language}/{number}`

Access: Private Admin

Headers:

```python
{"Authorization": "Bearer some api key"}
```

Params:

  - `language` = the language for the given hymn
  - `number` = the hymn number

Errors:

  - 404 - Not Found if language-number does not exist
  - 403 - Unauthorized if authorization token is not valid or was not supplied
  - 400 - Bad Request if request passed is invalid
  - 429 - Too many requests if user makes too many requests in a given amount of time

Request:

```python
class UpdateSongRequest(BaseModel):
    title: str
    key: MusicalNote
    lines: List[List[LineSection]]
```

Response: `Song`


#### Delete - DELETE `/{language}/{number}`

Access: Private Admin

Headers:

```python
{"Authorization": "Bearer some api key"}
```

Errors:

  - 404 - Not Found if language-number does not exist
  - 403 - Unauthorized if authorization token is not valid or was not supplied
  - 429 - Too many requests if user makes too many requests in a given amount of time

Response: `Song` - the song deleted
"""
from typing import Optional, List

from fastapi import FastAPI, Query, Security, HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.api_key import APIKeyHeader
from slowapi.middleware import SlowAPIMiddleware

import settings
from api.models import (
    Song,
    SongDetail,
    PaginatedResponse,
    PartialSong,
    Application,
    LoginResponse,
    OTPResponse,
    OTPRequest,
    User,
    convert_to_base_model,
    ChangePasswordRequest,
)
from api.utils import try_to
from services import hymns, config, auth

from services.auth import is_valid_api_key

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


api_key_header = APIKeyHeader(name="x-api-key")

hymns_service: Optional[hymns.types.HymnsService] = None
auth_service: Optional[auth.types.AuthService] = None
app = FastAPI()
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def _get_api_key(header_key: str = Security(api_key_header)):
    """Dependency for retrieving and validating the API key from the header or cookie"""
    if await is_valid_api_key(auth_service, header_key):
        return header_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="could not validate credentials"
    )


async def _get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Gets the current logged in user

    Args:
        token: the JWT token got from the oauth headers

    Returns:
        the User who is logged in

    Raises:
        raises HTTPException in case of any error
    """
    resp = await auth.get_current_user(auth_service, token=token)
    convert_to_user = try_to(User.from_auth)
    return convert_to_user(resp)


@app.middleware("http")
async def convert_ml_results(request: Request, call_next):
    """Converts any type that might be an ml.Result into its associated data"""
    response = await call_next(request)
    # try to convert each to the given value in response_model
    return try_to(convert_to_base_model)(response)


@app.on_event("startup")
async def start():
    """Initializes the hymns service"""
    db_path = settings.get_db_path()
    hymns_service_conf = settings.get_hymns_service_config()
    api_key_length = settings.get_api_key_length()
    api_secret = settings.get_api_secret()
    jwt_ttl = settings.get_jwt_ttl_in_sec()
    max_login_attempts = settings.get_max_login_attempts()
    mail_config = settings.get_email_config()
    mail_sender = settings.get_auth_email_sender()

    await config.save_service_config(db_path, hymns_service_conf)

    global hymns_service
    hymns_service = await hymns.initialize(db_path)

    global auth_service
    auth_service = await auth.initialize(
        root_path=db_path,
        key_size=api_key_length,
        api_secret=api_secret,
        jwt_ttl=jwt_ttl,
        max_login_attempts=max_login_attempts,
        mail_config=mail_config,
        mail_sender=mail_sender,
    )

    global app
    # API limiter
    app.state.limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[settings.get_rate_limit()],
        enabled=settings.get_is_rate_limit_enabled(),
    )


@app.post("/register", response_model=Application)
async def register_app():
    """Registers a new app to get a new API key.

    It returns the application with the raw key but saves a hashed key in the auth service
    such that an API key is seen only once
    """
    return await auth.register_app(auth_service)


@app.post("/login", response_model=LoginResponse)
async def login(data: OAuth2PasswordRequestForm = Depends()):
    """Logins in admin users"""
    otp_url = app.url_path_for(
        "verify_otp"
    )  # FIXME: When you add the admin site, change this to a proper HTML page
    return await auth.login(
        auth_service,
        username=data.username,
        password=data.password,
        otp_verification_url=otp_url,
    )


@app.post("/verify-otp", response_model=OTPResponse)
async def verify_otp(data: OTPRequest, token: str = Depends(oauth2_scheme)):
    """Verifies the one-time password got by email"""
    return await auth.verify_otp(auth_service, otp=data.otp, unverified_token=token)


@app.post("/change-password")
async def change_password(data: ChangePasswordRequest):
    """Initializes the password change process"""
    return await auth.change_password(auth_service, data=data)


@app.get("/{language}/{number}", response_model=SongDetail)
async def get_song_detail(
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


@app.get("/{language}/find-by-title/{q}", response_model=PaginatedResponse)
async def query_by_title(
    language: str,
    q: str,
    skip: int = 0,
    limit: int = 0,
    api_key: str = Security(_get_api_key),
):
    """Returns list of songs whose titles match the search term `q`"""
    return await hymns.query_songs_by_title(
        hymns_service, q=q, language=language, skip=skip, limit=limit
    )


@app.get("/{language}/find-by-number/{q}", response_model=PaginatedResponse)
async def query_by_number(
    language: str,
    q: int,
    skip: int = 0,
    limit: int = 0,
    api_key: str = Security(_get_api_key),
):
    """Returns list of songs whose numbers match the search term `q`"""
    return await hymns.query_songs_by_number(
        hymns_service, q=q, language=language, skip=skip, limit=limit
    )


@app.post("/", response_model=Song)
async def create_song(song: Song, user: User = Depends(_get_current_user)):
    """Creates a new song"""
    return await hymns.add_song(hymns_service, song=song.to_hymns_song())


@app.put("/{language}/{number}", response_model=Song)
async def update_song(
    language: str,
    number: int,
    song: PartialSong,
    user: User = Depends(_get_current_user),
):
    """Updates the song whose number is given"""
    original = await _get_song(language=language, number=number)
    new_data = {**original.dict(), **song.dict(exclude_unset=True)}
    new_song = Song(**new_data)
    return await hymns.add_song(hymns_service, song=new_song.to_hymns_song())


@app.delete("/{language}/{number}", response_model=Song)
async def delete_song(
    language: str, number: int, user: User = Depends(_get_current_user)
):
    """Deletes the song whose number is given"""
    return await hymns.delete_song(hymns_service, number=number, language=language)


async def _get_song(language: str, number: int) -> Song:
    """Gets the song for the given language and song number"""
    res = await hymns.get_song_by_number(
        hymns_service, number=number, language=language
    )
    convert_to_song = try_to(Song.from_hymns)
    return convert_to_song(res)
