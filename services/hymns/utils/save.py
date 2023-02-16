"""Utility functions and types for handling save to database operations"""
from typing import TYPE_CHECKING

from services.config import add_new_language
from services.utils import record_to_json
from services.hymns.models import Song
from .init import initialize_language_store

if TYPE_CHECKING:
    from ..data_types import LanguageStore, HymnsService


async def save_song(service: "HymnsService", song: Song) -> "HymnsService":
    """Saves the given song in the language store, both by the song number and song title.

    Args:
        service: the HymnsService instance to add song to
        song: the Song to add to the HymnsService

    Returns:
        The updated HymnsService
    """
    if song.language not in service.stores:
        service = await _save_new_language(service, lang=song.language)

    store = service.stores[song.language]
    await _save_to_titles_store(store, song=song)
    await _save_to_numbers_store(store, song=song)

    return service


async def _save_new_language(service: "HymnsService", lang: str) -> "HymnsService":
    """Saves the new language to the service and returns the updated service.

    Args:
        service: the HymnsService to which new language is to be added
        lang: the new language being added

    Returns:
        the updated HymnsService
    """
    await add_new_language(service.root_path, lang=lang)
    store = await initialize_language_store(service.root_path, lang=lang)
    service.stores[lang] = store
    return service


def _save_to_titles_store(store: LanguageStore, song: Song):
    """Saves song in language store by song title"""
    value = record_to_json(song)
    return store.titles_store.set(song.title, v=value)


def _save_to_numbers_store(store: LanguageStore, song: Song):
    """Saves song in language store by song number"""
    value = record_to_json(song)
    return store.titles_store.set(f"{song.number}", v=value)
