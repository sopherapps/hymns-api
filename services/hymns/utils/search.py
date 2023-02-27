"""Utility functions for handling search operations"""
from __future__ import annotations
from typing import TYPE_CHECKING

import funml as ml

if TYPE_CHECKING:
    from ..models import Song
    from ..types import LanguageStore


async def query_store_by_title(
    store: "LanguageStore", q: str, skip: int | None, limit: int | None
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
    payload = await store.titles_store.search(term=q, skip=skip, limit=limit)
    return [ml.from_json(Song, value=item) for _, item in payload]


async def query_store_by_number(
    store: "LanguageStore", q: int, skip: int | None, limit: int | None
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
    payload = await store.numbers_store.search(term=f"{q}", skip=skip, limit=limit)
    return [ml.from_json(Song, value=item) for _, item in payload]
