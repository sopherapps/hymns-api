"""Data Types used in the hymns service"""
from __future__ import annotations

from os import PathLike
from typing import TYPE_CHECKING, Optional

import funml as ml

import services
from services.store.base import Store

if TYPE_CHECKING:
    from services.config import ServiceConfig


@ml.record
class LanguageStore:
    """The collective store for the given language having all stores for that language.

    It includes two stores; one where the song titles are the keys and the other where
    the song numbers are the keys.

    Attributes:
        titles_store: the Store whose keys are the song titles
        numbers_store: the Store whose keys are the song numbers
    """

    language: str
    titles_store: Store
    numbers_store: Store


class HymnsService:
    """The Service for storing and manipulating hymns"""

    stores: dict[str, LanguageStore] = {}
    store_uri: bytes | PathLike[bytes] | str
    conf: "ServiceConfig"

    def __init__(
        self,
        root_path: bytes | PathLike[bytes] | str,
        stores: dict[str, LanguageStore] = {},
        conf: Optional["ServiceConfig"] = None,
    ):
        self.stores: dict[str, LanguageStore] = stores
        self.store_uri: bytes | PathLike[bytes] | str = root_path
        self.conf = services.config.ServiceConfig() if conf is None else conf
