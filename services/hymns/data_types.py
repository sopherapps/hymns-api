"""Data Types used in the hymns service"""
from typing import NamedTuple, Optional

import funml as ml
from py_scdb import AsyncStore

from services.hymns.models import Song


@ml.record
class LanguageStore:
    """The collective store for the given language having all stores for that language.

    It includes two stores; one where the song titles are the keys and the other where
    the song numbers are the keys.

    Attributes:
        titles_store: the AsyncStore whose keys are the song titles
        numbers_store: the AsyncStore whose keys are the song numbers
    """

    titles_store: AsyncStore
    numbers_store: AsyncStore


@ml.record
class HymnsService:
    """The Service for storing and manipulating hymns"""

    stores: dict[str, LanguageStore] = {}


class AddSongArgs(NamedTuple):
    """The type of parameter used when adding songs"""

    service: "HymnsService"
    song: Song

    def is_lang_available(self, *args) -> bool:
        """Checks whether the song language is available in the HymnsService"""
        return self.song.language in self.service.stores


class DeleteSongArgs(NamedTuple):
    """The type of parameter used when deleting songs"""

    service: "HymnsService"
    language: Optional[str] = None
    title: Optional[str] = None
    number: Optional[int] = None

    def is_lang_defined(self, *args) -> bool:
        """Checks Whether the language is defined or not"""
        return self.language is not None


class GetSongByTitleArgs(NamedTuple):
    """The type of parameter used when getting songs by title"""

    service: "HymnsService"
    language: str
    title: str


class GetSongByNumberArgs(NamedTuple):
    """The type of parameter used when getting songs by number"""

    service: "HymnsService"
    language: str
    number: int


class QuerySongByTitleArgs(NamedTuple):
    """The type of parameter used when searching for song title's beginning with."""

    service: "HymnsService"
    language: str
    q: str
    skip: int = 0
    limit: int = 20
