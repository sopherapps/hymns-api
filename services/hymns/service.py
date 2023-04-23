from __future__ import annotations

import funml as ml

import services
from services.hymns.utils.delete import delete_from_one_store, delete_from_all_stores
from services.hymns.utils.get import (
    get_song_by_number as get_raw_song_by_number,
    get_song_by_title as get_raw_song_by_title,
)
from services.hymns.utils.init import initialize_many_language_stores
from services.hymns.utils.save import save_song
from services.hymns.utils.search import (
    query_store_by_title,
    query_store_by_number,
)
from services.hymns.utils.shared import get_language_store
from services.hymns.models import Song, PaginatedResponse

from .types import HymnsService


async def initialize(
    config_db_uri: bytes | str, service_db_uri: bytes | str
) -> "HymnsService":
    """Initializes the hymns service given the configuration.

    Args:
        config_db_uri: the path to the store for the configuration service
        service_db_uri: the path to the stores for the hymns service

    Returns:
        the HymnsService whose configuration is at the store_uri
    """
    conf = await services.config.get_service_config(config_db_uri)
    stores = initialize_many_language_stores(service_db_uri, conf=conf)
    return HymnsService(root_path=service_db_uri, stores=stores)


async def add_song(service: "HymnsService", song: Song) -> ml.Result:
    """Adds a song to the hymns service and returns the newly added song as a ml.Result.OK.

    If any exception occurs, it returns ml.Result.ERR with that exception

    Args:
        service: the HymnsService that the song is to be added to
        song: the song to add to the hymns service

    Returns:
        an ml.Result.OK(Song) with the Song that has been added or an ml.Result.ERR(Exception) with the exception \
        that occurred
    """
    try:
        await save_song(service, song)
        return ml.Result.OK(song)
    except Exception as exp:
        return ml.Result.ERR(exp)


async def delete_song(
    service: "HymnsService",
    title: str | None = None,
    number: int | None = None,
    language: str | None = None,
) -> ml.Result:
    """Deletes the song of the given number or title

    If neither title nor number are provided, an ml.Result.ERR will be returned with a ValidationError.
    If not found, it will return a NotFoundError

    Args:
        service: the HymnsService from which to delete the song
        title: the title of the song to delete. It can be None if number is provided. Default is None.
        number: the song number to delete. It can be None if title is provided. Default is None.
        language: the language from which to delete the song. If None, the song is deleted from all languages. Default: None

    Returns:
        an ml.Result.OK(List[Song]) with songs that have been deleted or an ml.Result.ERR(Exception) with the exception \
        that occurred
    """
    try:
        if language is None:
            songs = await delete_from_all_stores(service, title=title, number=number)
            return ml.Result.OK(songs)
        else:
            store = get_language_store(service, lang=language)
            songs = await delete_from_one_store(store, title=title, number=number)
            return ml.Result.OK(songs)
    except Exception as exp:
        return ml.Result.ERR(exp)


async def get_song_by_title(
    service: "HymnsService", title: str, language: str
) -> ml.Result:
    """Gets a song by title and language.

    Args:
        service: the HymnsService from which to get the song
        title: the title of the song to retrieve
        language: the language the song is in

    Returns:
        an ml.Result.OK(Song) with the Song that has been got or an ml.Result.ERR(Exception) with the exception
        that occurred
    """
    try:
        store = get_language_store(service, lang=language)
        song = await get_raw_song_by_title(store, title=title)
        return ml.Result.OK(song)
    except Exception as exp:
        return ml.Result.ERR(exp)


async def get_song_by_number(
    service: "HymnsService", number: int, language: str
) -> ml.Result:
    """Gets a song by song number and language.

    Args:
        service: the HymnsService from which to get the song
        number: the song number of the song to retrieve
        language: the language the song is in

    Returns:
        an ml.Result.OK(Song) with the Song that has been got or an ml.Result.ERR(Exception) with the exception \
        that occurred
    """
    try:
        store = get_language_store(service, lang=language)
        song = await get_raw_song_by_number(store, number=number)
        return ml.Result.OK(song)
    except Exception as exp:
        return ml.Result.ERR(exp)


async def query_songs_by_title(
    service: "HymnsService",
    q: str,
    language: str,
    skip: int = 0,
    limit: int = 0,
) -> ml.Result:
    """Gets a list of songs in the given language whose title starts with the given `q`.

    Args:
        service: the HymnsService that has the data
        q: the search term
        language: the language the songs are to be expected in
        skip: the number of matching items to skip before starting to return
        limit: the maximum number of songs to return in the query

    Returns:
        an ml.Result.OK(PaginatedResponse(data=List[Song], skip=int, limit=int)) with songs that have matched within \
        the limits or an ml.Result.ERR(Exception) with the exception that occurred
    """
    try:
        store = get_language_store(service, lang=language)
        songs = await query_store_by_title(store, q=q, skip=skip, limit=limit)
        return ml.Result.OK(PaginatedResponse(data=songs, skip=skip, limit=limit))
    except Exception as exp:
        return ml.Result.ERR(exp)


async def query_songs_by_number(
    service: "HymnsService",
    q: int,
    language: str,
    skip: int = 0,
    limit: int = 0,
) -> ml.Result:
    """Gets a list of songs in the given language whose number starts with the given `q`.

    Args:
        service: the HymnsService that has the data
        q: the search term
        language: the language the songs are to be expected in
        skip: the number of matching items to skip before starting to return
        limit: the maximum number of songs to return in the query

    Returns:
        an ml.Result.OK(PaginatedResponse(data=List[Song], skip=int, limit=int)) with songs that have matched within \
        the limits or an ml.Result.ERR(Exception) with the exception that occurred
    """
    try:
        store = get_language_store(service, lang=language)
        songs = await query_store_by_number(store, q=q, skip=skip, limit=limit)
        return ml.Result.OK(PaginatedResponse(data=songs, skip=skip, limit=limit))
    except Exception as exp:
        return ml.Result.ERR(exp)
