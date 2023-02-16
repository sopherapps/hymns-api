"""Utility functions for handling initializing the service"""
from __future__ import annotations

from os import PathLike

from typing import TYPE_CHECKING, Dict

from services.config import get_numbers_store, get_titles_store
from services.hymns.data_types import LanguageStore

if TYPE_CHECKING:
    from ...config import ServiceConfig


async def initialize_language_stores(
    root_path: bytes | PathLike[bytes] | str, conf: ServiceConfig
) -> Dict[str, LanguageStore]:
    """Initializes the dictionary of languages and their stores in the config.

    Args:
        root_path: the path to where the store is to be found
        conf: the ServiceConfig for the current service

    Returns:
        a dictionary showing the languages and their stores
    """
    return {
        lang: (await initialize_language_store(root_path, lang))
        for lang in conf.languages
    }


async def initialize_language_store(
    root_path: bytes | PathLike[bytes] | str, lang: str
) -> LanguageStore:
    """Initializes the LanguageStore for the given language.

    Args:
        root_path: the path where the stores are to be found
        lang: the language name whose store is to be retrieved

    Returns:
        the LanguageStore that corresponds to the given language
    """
    numbers_store = await get_numbers_store(root_path, lang=lang)
    titles_store = await get_titles_store(root_path, lang=lang)
    return LanguageStore(
        numbers_store=numbers_store, titles_store=titles_store, language=lang
    )
