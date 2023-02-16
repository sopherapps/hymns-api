"""Data Types used in the hymns service"""
from __future__ import annotations

from os import PathLike

import funml as ml
from py_scdb import AsyncStore


@ml.record
class LanguageStore:
    """The collective store for the given language having all stores for that language.

    It includes two stores; one where the song titles are the keys and the other where
    the song numbers are the keys.

    Attributes:
        titles_store: the AsyncStore whose keys are the song titles
        numbers_store: the AsyncStore whose keys are the song numbers
    """

    language: str
    titles_store: AsyncStore
    numbers_store: AsyncStore


@ml.record
class HymnsService:
    """The Service for storing and manipulating hymns"""

    stores: dict[str, LanguageStore] = {}
    root_path: bytes | PathLike[bytes] | str
