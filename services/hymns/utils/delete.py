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
) -> list[Song]:
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
            songs += await delete_from_one_store(store, title=title, number=number)
        except NotFoundError:
            pass

    if len(songs) == 0:
        msg = f"song title '{title}'" if title is not None else f"song number {number}"
        raise NotFoundError(msg)

    return songs


async def delete_from_one_store(
    store: "LanguageStore", title: str | None, number: int | None
) -> list["Song"]:
    """Removes the song of given title or number from the language store.

    Args:
        store: the LanguageStore from which to delete the song
        title: the title of the song to delete
        number: the song number of the song to delete

    Returns:
        the deleted songs

    Raises:
        NotFoundError: no song of title or number was found
        ValidationError: no title or number supplied for deletion
    """
    err_msg = ""
    deleted_songs = {}
    is_title_defined = title is not None
    is_number_defined = number is not None

    if not is_title_defined and not is_number_defined:
        raise ValidationError("no title or number supplied for deletion")

    if is_title_defined:
        songs = await store.titles_store.delete(title)
        songs_map = {
            f"{song.number}-{song.title}-{song.language}": song for song in songs
        }
        deleted_songs = {**songs_map}
        err_msg += f"title {title}, "

    if is_number_defined:
        songs = await store.numbers_store.delete(f"{number}")
        songs_map = {
            f"{song.number}-{song.title}-{song.language}": song for song in songs
        }
        deleted_songs = {**deleted_songs, **songs_map}
        err_msg += f"number {number}, "

    if len(deleted_songs) > 0:
        return [*deleted_songs.values()]

    raise NotFoundError(f"{err_msg}for language: '{store.language}'")


async def _delete_from_titles_store(
    store: "LanguageStore", title: str | None
) -> list[Song] | None:
    """Removes song from titles store of language store"""
    if title is not None:
        return await store.titles_store.delete(title)


async def _delete_from_numbers_store(
    store: "LanguageStore", number: int | None
) -> list[Song] | None:
    """Removes song from numbers store of language store"""
    if number is not None:
        return await store.numbers_store.delete(f"{number}")
