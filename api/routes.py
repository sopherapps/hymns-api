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
  - 401 - Unauthorized if API key is not valid or was not supplied
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

- 401 - Unauthorized if API Key is not valid or was not supplied
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
  - 401 - Unauthorized if authorization token is not valid or was not supplied
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
  - 401 - Unauthorized if authorization token is not valid or was not supplied
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
  - 401 - Unauthorized if authorization token is not valid or was not supplied
  - 429 - Too many requests if user makes too many requests in a given amount of time

Response: `Song` - the song deleted
"""
from typing import Optional, List

from fastapi import FastAPI, Query, Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
import funml as ml
from slowapi.middleware import SlowAPIMiddleware

import settings
from api.models import Song, SongDetail, PaginatedResponse, PartialSong, Application
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


async def _get_api_key(header_key: str = Security(api_key_header)):
    """Dependency for retrieving and validating the API key from the header or cookie"""
    if await is_valid_api_key(auth_service, header_key):
        return header_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="could not validate credentials"
    )


@app.on_event("startup")
async def start():
    """Initializes the hymns service"""
    db_path = settings.get_db_path()
    hymns_service_conf = settings.get_hymns_service_config()
    api_key_length = settings.get_api_key_length()

    await config.save_service_config(db_path, hymns_service_conf)

    global hymns_service
    hymns_service = await hymns.initialize(db_path)

    global auth_service
    auth_service = await auth.initialize(root_path=db_path, key_size=api_key_length)

    global app
    # API limiter
    app.state.limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[settings.get_rate_limit()],
        enabled=settings.get_is_rate_limit_enabled(),
    )


@app.post("/register", response_model=Application)
async def register():
    """Registers a new app to get a new API key.

    It returns the application with the raw key but saves a hashed key in the auth service
    such that an API key is seen only once
    """
    res = await auth.register_app(auth_service)
    convert_to_application = try_to(Application.from_hymns)
    return convert_to_application(res)


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
    res = await hymns.query_songs_by_title(
        hymns_service, q=q, language=language, skip=skip, limit=limit
    )
    convert_to_paginated_resp = try_to(PaginatedResponse.from_hymns)
    return convert_to_paginated_resp(res)


@app.get("/{language}/find-by-number/{q}", response_model=PaginatedResponse)
async def query_by_number(
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
    convert_to_paginated_resp = try_to(PaginatedResponse.from_hymns)
    return convert_to_paginated_resp(res)


@app.post("/", response_model=Song)
async def create_song(song: Song, api_key: str = Security(_get_api_key)):
    """Creates a new song"""
    return await _save_song(song)


@app.put("/{language}/{number}", response_model=Song)
async def update_song(
    language: str, number: int, song: PartialSong, api_key: str = Security(_get_api_key)
):
    """Updates the song whose number is given"""
    original = await _get_song(language=language, number=number)
    new_data = {**original.dict(), **song.dict(exclude_unset=True)}
    new_song = Song(**new_data)
    return await _save_song(new_song)


@app.delete("/{language}/{number}", response_model=Song)
async def delete_song(
    language: str, number: int, api_key: str = Security(_get_api_key)
):
    """Deletes the song whose number is given"""
    res = await hymns.delete_song(hymns_service, number=number, language=language)
    convert_to_song_list = try_to(ml.imap(Song.from_hymns))
    deleted_songs = convert_to_song_list(res)
    return deleted_songs[0]


async def _save_song(song: Song):
    """Saves the song in the database"""
    res = await hymns.add_song(hymns_service, song=song.to_hymns_song())
    convert_to_song = try_to(Song.from_hymns)
    return convert_to_song(res)


async def _get_song(language: str, number: int) -> Song:
    """Gets the song for the given language and song number"""
    res = await hymns.get_song_by_number(
        hymns_service, number=number, language=language
    )
    convert_to_song = try_to(Song.from_hymns)
    return convert_to_song(res)
