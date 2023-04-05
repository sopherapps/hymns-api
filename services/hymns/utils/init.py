"""Utility functions for handling initializing the service"""
from __future__ import annotations

from os import PathLike

from typing import TYPE_CHECKING, Dict

import services
from services.hymns.types import LanguageStore

if TYPE_CHECKING:
    from ...config import ServiceConfig


def initialize_many_language_stores(
    uri: bytes | PathLike[bytes] | str, conf: ServiceConfig
) -> Dict[str, LanguageStore]:
    """Initializes the dictionary of languages and their stores in the config.

    Args:
        uri: the path to where the store is to be found
        conf: the ServiceConfig for the current service

    Returns:
        a dictionary showing the languages and their stores
    """
    return {
        lang: initialize_one_language_store(conf=conf, uri=uri, lang=lang)
        for lang in conf.languages
    }


def initialize_one_language_store(
    conf: ServiceConfig, uri: bytes | PathLike[bytes] | str, lang: str
) -> LanguageStore:
    """Initializes the LanguageStore for the given language.

    Args:
        conf: the ServiceConfig for the current service
        uri: the path where the stores are to be found
        lang: the language name whose store is to be retrieved

    Returns:
        the LanguageStore that corresponds to the given language
    """
    numbers_store = services.config.get_numbers_store(
        service_conf=conf, uri=uri, lang=lang
    )
    titles_store = services.config.get_titles_store(
        service_conf=conf, uri=uri, lang=lang
    )
    return LanguageStore(
        numbers_store=numbers_store, titles_store=titles_store, language=lang
    )
