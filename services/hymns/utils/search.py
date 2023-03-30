"""Utility functions for handling search operations"""
from __future__ import annotations
from typing import TYPE_CHECKING

import funml as ml
from ..models import Song

if TYPE_CHECKING:
    from ..types import LanguageStore


async def query_store_by_title(
    store: "LanguageStore", q: str, skip: int = 0, limit: int = 0
) -> list[Song]:
    """Gets a list of songs whose titles begin with the search term.

    Args:
        store: the LanguageStore where the songs are found
        q: the search term
        skip: the number of matching items to skip before starting to return
        limit: the maximum number of items to return at a go

    Returns:
        a list of matching songs for the given search term in the given store
    """
    return await store.titles_store.search(Song, term=q, skip=skip, limit=limit)


async def query_store_by_number(
    store: "LanguageStore", q: int, skip: int = 0, limit: int = 0
) -> list[Song]:
    """Gets a list of songs whose song numbers begin with the search term.

    Args:
        store: the LanguageStore where the songs are found
        q: the search term
        skip: the number of matching items to skip before starting to return
        limit: the maximum number of items to return at a go

    Returns:
        a list of matching songs for the given search term in the given store
    """
    return await store.numbers_store.search(Song, term=f"{q}", skip=skip, limit=limit)
