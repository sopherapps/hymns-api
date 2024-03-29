"""Utility functions and types for handling save to database operations"""
from typing import TYPE_CHECKING

import services
from services.hymns.models import Song
from .init import initialize_one_language_store

if TYPE_CHECKING:
    from ..types import LanguageStore, HymnsService


async def save_song(service: "HymnsService", song: Song):
    """Saves the given song in the language store, both by the song number and song title.

    The service is mutated.

    Args:
        service: the HymnsService instance to add song to
        song: the Song to add to the HymnsService
    """
    if song.language not in service.stores:
        await _save_new_language(service, lang=song.language)

    store = service.stores[song.language]
    await _save_to_titles_store(store, song=song)
    await _save_to_numbers_store(store, song=song)


async def _save_new_language(service: "HymnsService", lang: str):
    """Saves the new language to the service and returns the updated service.

    It mutates the HymnsService instance

    Args:
        service: the HymnsService to which new language is to be added
        lang: the new language being added
    """
    await services.config.add_new_language_in_place(
        service_conf=service.conf, uri=service.store_uri, lang=lang
    )
    store = initialize_one_language_store(
        conf=service.conf, uri=service.store_uri, lang=lang
    )
    service.stores[lang] = store


def _save_to_titles_store(store: "LanguageStore", song: Song):
    """Saves song in language store by song title"""
    return store.titles_store.set(k=song.title, v=song)


def _save_to_numbers_store(store: "LanguageStore", song: Song):
    """Saves song in language store by song number"""
    return store.numbers_store.set(k=f"{song.number}", v=song)
