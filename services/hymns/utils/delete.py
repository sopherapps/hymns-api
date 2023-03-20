"""Utility functions for handling delete operations"""
from __future__ import annotations
from typing import TYPE_CHECKING

import funml as ml

from services.hymns.errors import ValidationError
from ...errors import NotFoundError

from .get import get_song_by_title_or_number

if TYPE_CHECKING:
    from ..types import LanguageStore, HymnsService
    from ..models import Song


async def delete_from_all_stores(
    service: "HymnsService", title: str | None, number: int | None
) -> ml.IList[Song]:
    """Removes the song of given title or number from all language stores.

    Raises:
        ValidationError: when no title or number is supplied for deletion
        NotFoundError: when song is not found in any language store

    Returns:
        list of songs that have been deleted
    """
    if title is None and number is None:
        raise ValidationError("no title or number supplied for deletion")

    songs = []
    for store in service.stores.values():
        try:
            song = await delete_from_one_store(store, title=title, number=number)
            songs.append(song)
        except NotFoundError:
            pass

    if len(songs) == 0:
        msg = f"song title '{title}'" if title is not None else f"song number {number}"
        raise NotFoundError(msg)

    return ml.l(*songs)


async def delete_from_one_store(
    store: "LanguageStore", title: str | None, number: int | None
) -> "Song":
    """Removes the song of given title or number from the language store.

    Args:
        store: the LanguageStore from which to delete the song
        title: the title of the song to delete
        number: the song number of the song to delete

    Returns:
        the deleted song

    Raises:
        NotFoundError: no song of title or number was found
    """
    song = await get_song_by_title_or_number(store, title=title, number=number)
    if song is None:
        msg = f"song title: {title}" if title is not None else f"song number: {number}"
        raise NotFoundError(f"{msg} for language: '{store.language}'")

    await _delete_from_titles_store(store, title=song.title)
    await _delete_from_numbers_store(store, number=song.number)

    return song


async def _delete_from_titles_store(store: "LanguageStore", title: str | None):
    """Removes song from titles store of language store"""
    if title is not None:
        await store.titles_store.delete(title)


async def _delete_from_numbers_store(store: "LanguageStore", number: int | None):
    """Removes song from numbers store of language store"""
    if number is not None:
        await store.numbers_store.delete(f"{number}")
