# Hymns API

This is a general API that can host hymns/songs including their musical notation.

## Notable Features:

 - Rate limited API
 - Publicly available READ-ONLY with need for an API Key
 - Privately accessible WRITE-ONLY with need of a JWT auth token for admins only
 - Very fast, due to use of embedded document-oriented database
 - Can have multiple translations for each song
 - CLI to do some devOps chores e.g. create new admin users etc.

## Contributing

Contributions are welcome. The docs have to maintained, the code has to be made cleaner, more idiomatic and faster,
and there might be need for someone else to take over this repo in case I move on to other things. It happens!

When you are ready, look at the [CONTRIBUTIONS GUIDELINES](./CONTRIBUTING.md)

## System Design

### Dependencies

- [Python v3.11+](https://python.org) - the programming language
- [FastAPI](https://fastapi.tiangolo.com/) - web server
- [Typer CLI](https://typer.tiangolo.com/typer-cli/) - for CLI commands
- [py_scdb](https://github.com/sopherapps/py_scdb) - embedded database
- [slowapi](https://pypi.org/project/slowapi/) - rate-limiting

### Main Persisted Data Structure

```python
"""
class Language(Enum):
    RUNYORO = 'runyoro'
    ENGLISH = 'english'
    SWEDISH = 'swedish'
    ...
    
    def __str__(self):
        return self.value
    
class MusicalNote(Enum):
    C_MAJOR = 'C'
    C_MINOR = 'Cm'
    C_SHARP_MAJOR = 'C#'
    C_SHARP_MINOR = 'C#m'
    ...
    
    def __str__(self):
        return self.value
    

class LineSection(BaseModel):
    note: MusicalNote
    words: str
"""  

class Song(BaseModel):
    number: int 
    language: Language
    title: str 
    key: MusicalNote
    lines: List[List[LineSection]]

    @property
    def id(self) -> str:
        """language-number combination is unique id"""
        return f"{self.language}-{self.number}"
```

### Main CLI commands

#### Run App

```shell
python manage.py run --port your-port --rate-limit-per-minute your-rate-limit-per-minute
```

Errors:

  - port already in use 

#### Create Admin User

```shell
python manage.py create_admin --email your-email --password your-password
```

Errors:

  - email already exists [Creating new passwords is manual for now -- i.e. delete user first]

#### Delete Admin User

```shell
python manage.py delete_admin --email your-email --password your-password
```

Errors:

  - email does not exist

### Main API Requests

#### Admin Login - POST `/login`

Access: Public

Errors:

  - 401 - Conflict if email and password don't match
  - 429 - Too many requests if user makes too many requests in a given amount of time
  - 400 - Bad Request if request passed is invalid

Request:

```python
class LoginRequest(BaseModel):
    email: str
    password: str
```

Response:

```python
class LoginResponse(BaseModel):
    access_token: str
```


#### Register - POST `/register`

Access: Public

Errors:

  - 409 - Conflict if email already exists [Handling API key regeneration is manual for now]
  - 429 - Too many requests if user makes too many requests in a given amount of time
  - 400 - Bad Request if request passed is invalid

Request:

```python
class RegistrationRequest(BaseModel):
    email: str
```

Response:

```python
class RegistrationResponse(BaseModel):
    api_key: str
```


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
"""
SongTitle = str

class SongItem(BaseModel):
    number: int 
    translations: Dict[Language, SongTitle]
"""

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

### Other Design Decisions

- Each translation has its own scdb database, for scalability.
- The `user` records are in their own scdb database, for scalability.
- Access to different databases is done concurrently, for more speed.
- All business logic is put in appropriate services in the `services` folder
- All API related logic is in the `api` package, entry point being `main.py` in root folder.
- All CLI(command line interface) related logic is in the `cli` package, 
  entry point being `manage.py` in root folder.
- Any shared utility functions are found in the `utils` package or module in the package where
  they are needed e.g. services can have its own `utils`, api can also have its own `utils`,
  even the entire project can have its own `utils`.
- The `tests` package mirrors the folder structure followed by the project, 
  but with `test_` prefixes on the module names.

## Acknowledgements

- Century Publishing House Ltd published the version from which most of these hymns are got.

## License

Copyright (c) 2023 [Martin Ahindura](https://github.com/Tinitto) Licensed under the [MIT License](./LICENSE)

## Gratitude

> "Sing to the Lord!
>    Give praise to the Lord!
>  He rescues the life of the needy
>    from the hands of the wicked."
>
> -- Jeremiah 20: 13

All glory be to God

<a href="https://www.buymeacoffee.com/martinahinJ" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
