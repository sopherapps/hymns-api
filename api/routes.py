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
from typing import Optional, List, Any

from fastapi import FastAPI, Query
import funml as ml

import settings
from api.models import Song, SongDetail, PaginatedResponse, PartialSong
from api.utils import raise_http_error
from services import hymns, config

hymns_service: Optional[hymns.types.HymnsService] = None
app = FastAPI()


@app.on_event("startup")
async def start():
    """Initializes the hymns service"""
    await config.save_service_config(settings.DB_PATH, settings.HYMNS_SERVICE_CONFIG)
    global hymns_service
    hymns_service = await hymns.initialize(settings.DB_PATH)


@app.get("/{language}/{number}", response_model=SongDetail)
async def get_song_detail(
    language: str, number: int, translation: List[str] = Query(default=())
):
    """Displays the details of the song whose number is given"""
    languages = [language, *translation]
    song = SongDetail(number=number, translations={})

    for lang in languages:
        res = await hymns.get_song_by_number(
            hymns_service, number=number, language=lang
        )

        _translation = (
            ml.match()
            .case(ml.Result.OK(Any), do=Song.from_hymns_song)
            .case(ml.Result.ERR(Exception), do=raise_http_error)(res)
        )

        song.translations[lang] = _translation

    return song


@app.get("/{language}/find-by-title/{q}", response_model=PaginatedResponse)
async def query_by_title(
    language: str,
    q: str,
    page: int = 0,
    limit: int = 0,
    translations: Optional[List[str]] = (),
):
    """Returns list of songs whose titles match the search term `q`"""
    pass


@app.get("/{language}/find-by-number/{q}", response_model=PaginatedResponse)
async def query_by_number(
    language: str,
    q: int,
    page: int = 0,
    limit: int = 0,
    translations: Optional[List[str]] = (),
):
    """Returns list of songs whose numbers match the search term `q`"""
    pass


@app.post("/", response_model=Song)
async def create_song(song: Song):
    """Creates a new song"""
    res = await hymns.add_song(hymns_service, song=song.to_hymns_song())
    return (
        ml.match()
        .case(ml.Result.OK(Any), do=Song.from_hymns_song)
        .case(ml.Result.ERR(Exception), do=raise_http_error)(res)
    )


@app.put("/{language}/{number}", response_model=Song)
async def update_song(language: str, number: int, song: PartialSong):
    """Updates the song whose number is given"""
    pass


@app.delete("/{language}/{number}", response_model=Song)
async def delete_song(language: str, number: int):
    """Deletes the song whose number is given"""
    pass
