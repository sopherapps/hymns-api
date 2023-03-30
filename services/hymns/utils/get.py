"""Utility functions for handling get operations"""
from __future__ import annotations
from typing import TYPE_CHECKING

import funml as ml
from services.hymns.models import Song
from ..errors import ValidationError
from ...errors import NotFoundError

if TYPE_CHECKING:
    from ..types import LanguageStore


async def get_song_by_title(store: "LanguageStore", title: str) -> Song:
    """Gets a given song by number from the given language store.

    Args:
        store: the LanguageStore in which the songs are found
        title: the song title of the song to retrieve

    Returns:
        the Song whose title is the `title` provided

    Raises:
        services.hymns.errors.NotFoundError: song of given title not found for given language
    """
    song = await store.titles_store.get(Song, title)

    if song is None:
        raise NotFoundError(
            f"song of title: '{title}' for language: '{store.language}'"
        )

    return song


async def get_song_by_number(store: "LanguageStore", number: int) -> Song:
    """Gets a given song by number from the given language store.

    Args:
        store: the LanguageStore in which the songs are found
        number: the song number of the song to retrieve

    Returns:
        the Song whose song number is the `number` provided

    Raises:
        services.hymns.errors.NotFoundError: song of given number not found for given language
    """
    song = await store.numbers_store.get(Song, f"{number}")

    if song is None:
        raise NotFoundError(
            f"song of number: '{number}' not found for language: '{store.language}'"
        )

    return song


async def get_song_by_title_or_number(
    store: "LanguageStore", title: str | None = None, number: int | None = None
) -> Song:
    """Gets a song by either title or number.

    If both title and number are provided, only the title is considered.

    Args:
        store: the LanguageStore from which to get the song
        title: the title of the song
        number: the song number of the song

    Returns:
        the Song of the given title or number.

    Raises:
        ValidationError: no title or number provided to identify the song
    """
    if title is not None:
        return await get_song_by_title(store, title=title)
    elif number is not None:
        return await get_song_by_number(store, number=number)

    raise ValidationError("no title or number provided to identify the song")
