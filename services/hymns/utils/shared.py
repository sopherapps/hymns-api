"""Utilities common to many operations"""
from typing import TYPE_CHECKING

import funml as ml

from ...errors import NotFoundError
from ...types import MusicalNote

if TYPE_CHECKING:
    from ..types import HymnsService


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
