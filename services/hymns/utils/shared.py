"""Utilities common to many operations"""
import json
from typing import TYPE_CHECKING

from services.hymns.errors import NotFoundError
from services.hymns.models import Song

if TYPE_CHECKING:
    from ..data_types import HymnsService


def convert_json_to_song(data: str) -> Song:
    """Converts a JSON string into a Song.

    Args:
        data: the JSON representation of the song

    Returns:
        the Song represented by `data`
    """
    return Song(**json.loads(data))


def get_language_store(service: "HymnsService", lang: str):
    """Gets the language store for the given language from the service

    Args:
        service: the HymnsService from which the language store is to be got
        lang: the language of the store to be got

    Raises:
        NotFoundError: no such language found
    """
    try:
        return service.stores[lang]
    except KeyError:
        raise NotFoundError(f"no such language as {lang}")
