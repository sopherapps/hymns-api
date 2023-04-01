"""Storage in py_scdb"""
from __future__ import annotations

import dataclasses
import json
from os import path
from typing import List, Optional, Type, TypeVar, Dict, Tuple, Any

import funml as ml
import py_scdb
from pydantic import BaseModel

from .base import Store
from .utils.collections import get_store_language_and_pk_field
from ..utils import Config

T = TypeVar("T", bound=BaseModel)


class ScdbConfig(Config):
    max_keys: int = 2_000_000
    redundant_blocks: int = 2
    pool_capacity: int = 5
    is_search_enabled: bool = False


class Event(ml.Enum):
    SET = Tuple[str, BaseModel]
    GET = str
    DEL = BaseModel
    CLEAR = None


@dataclasses.dataclass
class Observer:
    pk_field: str
    store: py_scdb.AsyncStore

    async def handle_event(self, ev: Event):
        """Handles the event self is subscribed to"""
        return await (
            ml.match()
            .case(
                Event.DEL(BaseModel),
                do=lambda v: self.store.delete(f"{getattr(v, self.pk_field)}"),
            )
            .case(Any, do=nothing)(ev)
        )


class ScdbStore(Store[T]):
    """Storage class implemented using py_scdb"""

    __store_type__: str = "scdb"
    __store_config_cls__: Type[ScdbConfig] = ScdbConfig
    __observer_registry__: Dict[str, Dict[str, Observer]] = {}

    def __init__(self, uri: str, name: str, model: Type[T], options: ScdbConfig):
        super().__init__(uri, name, model, options)
        store_path = path.join(uri, name)
        self.__store = py_scdb.AsyncStore(store_path=store_path, **dict(options))

        self.__lang, pk_field = get_store_language_and_pk_field(name)
        self.__store_path = store_path

        if self.__lang:
            lang_subscribers = ScdbStore.__observer_registry__.setdefault(
                self.__lang, {}
            )
            lang_subscribers[store_path] = Observer(
                store=self.__store, pk_field=pk_field
            )

    def __del__(self):
        try:
            del ScdbStore.__observer_registry__[self.__lang][self.__store_path]
        except KeyError:
            pass

    async def set(self, k: str, v: T, **kwargs) -> None:
        return await self.__store.set(k, v.json())

    async def get(self, k: str) -> Optional[T]:
        value = await self.__store.get(k)
        if isinstance(value, str):
            return self._model(**json.loads(value))

    async def search(self, term: str, skip: int = 0, limit: int = 0) -> List[T]:
        results = await self.__store.search(term=term, skip=skip, limit=limit)
        return [self._model(**json.loads(v)) for k, v in results]

    async def delete(self, k: str) -> List[T]:
        value = await self.get(k)
        if isinstance(value, self._model):
            if self.__lang:
                await self.__send_event(Event.DEL(value))
            else:
                await self.__store.delete(k)
            return [value]
        return []

    async def clear(self) -> None:
        return await self.__store.clear()

    @staticmethod
    async def _clean_up():
        pass

    async def __send_event(self, ev: Event):
        """Tries to send the event to the observer registry"""
        observers = ScdbStore.__observer_registry__.get(self.__lang, {}).values()

        for observer in observers:
            await observer.handle_event(ev)


async def nothing(*args):
    """do nothing"""
    pass
