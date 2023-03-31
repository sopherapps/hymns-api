"""Storage in py_scdb"""
from __future__ import annotations

import json
from os import path
from typing import List, Optional, Type, TypeVar

import py_scdb
from pydantic import BaseModel

from .base import Store
from ..utils import Config

T = TypeVar("T", bound=BaseModel)


class ScdbConfig(Config):
    max_keys: int = 2_000_000
    redundant_blocks: int = 2
    pool_capacity: int = 5
    is_search_enabled: bool = False


class ScdbStore(Store):
    """Storage class implemented using py_scdb"""

    __store_type__: str = "scdb"
    __store_config_cls__: Type[ScdbConfig] = ScdbConfig

    def __init__(self, uri: str, name: str, options: ScdbConfig):
        super().__init__(uri, name, options)
        store_path = path.join(uri, name)
        self.__store = py_scdb.AsyncStore(store_path=store_path, **dict(options))

    async def set(self, k: str, v: BaseModel, **kwargs) -> None:
        return await self.__store.set(k, v.json())

    async def get(self, model: Type[T], k: str) -> Optional[T]:
        value = await self.__store.get(k)
        if isinstance(value, str):
            return model(**json.loads(value))

    async def search(
        self, model: Type[T], term: str, skip: int = 0, limit: int = 0
    ) -> List[T]:
        results = await self.__store.search(term=term, skip=skip, limit=limit)
        return [model(**json.loads(v)) for k, v in results]

    async def delete(self, k: str) -> None:
        return await self.__store.delete(k)

    async def clear(self) -> None:
        return await self.__store.clear()

    @staticmethod
    async def _clean_up():
        pass

    @staticmethod
    async def _initialize_store():
        pass
