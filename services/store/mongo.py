"""Storage in mongodb"""
import dataclasses
from typing import TypeVar, Type, List, Optional, Dict, Any

import pymongo
from pydantic import BaseModel
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)

from services.store import Store
from services.store.utils.collections import (
    get_store_language_and_pk_field,
    get_table_name,
    get_pk_fields,
)
from services.utils import Config

T = TypeVar("T", bound=BaseModel)


class MongoConfig(Config):
    db_name: str = "data"

    def get_conn_config(self) -> Dict[str, Any]:
        """Gets the configuration for creating connections"""
        conf = self.dict(exclude_none=True)
        del conf["db_name"]
        return conf


@dataclasses.dataclass
class MongoConnection:
    """A motor Mongo Client with its meta data"""

    client: AsyncIOMotorClient
    databases: Dict[str, AsyncIOMotorDatabase] = dataclasses.field(default_factory=dict)


class MongoStore(Store[T]):
    """Storage class implemented using mongodb"""

    __store_type__: str = "mongodb"
    __store_config_cls__: Type[Config] = MongoConfig
    __clients__: Dict[str, AsyncIOMotorClient] = {}

    def __init__(self, uri: str, name: str, model: Type[T], options: MongoConfig):
        super().__init__(uri, name, model, options)

        conn_conf = options.get_conn_config()
        self.__name = name
        self.__uri = uri
        self.__database_name = options.db_name
        self.__collection_name = get_table_name(name)
        self._lang, self._search_field = get_store_language_and_pk_field(name)
        self.__pk_fields = get_pk_fields(self.__collection_name)

        self.__register_client_if_not_exists(conn_conf)
        self.__create_search_index_if_not_exists(conn_conf)

    @property
    def _collection(self) -> AsyncIOMotorCollection:
        """The collection associated with this store"""
        return MongoStore.__clients__[self.__uri][self.__database_name][
            self.__collection_name
        ]

    async def set(self, k: str, v: T, **kwargs) -> None:
        query = {}
        data = v.dict()
        data[self._search_field] = k

        for pk_field in self.__pk_fields:
            pk_value = data.get(pk_field, None)
            query[pk_field] = pk_value
            data[pk_field] = f"{pk_value}"

        await self._collection.update_one(
            filter=query, update={"$set": data}, upsert=True
        )

    async def get(self, k: str) -> Optional[T]:
        query = self.__get_query(k)
        value = await self._collection.find_one(query)
        if value is not None:
            return self._model(**value)

    async def search(self, term: str, skip: int = 0, limit: int = 0) -> List[T]:
        length = None
        query = self.__get_query(term, is_regex=True)
        cursor = self._collection.find(query)
        cursor.skip(skip)
        if limit > 0:
            cursor.limit(limit)
            length = limit

        results = await cursor.to_list(length)
        return [self._model(**item) for item in results]

    async def delete(self, k: str) -> List[T]:
        query = self.__get_query(k)
        matched_items = await self._collection.find(query).to_list(length=None)
        await self._collection.delete_many(query)
        return [self._model(**item) for item in matched_items]

    async def clear(self) -> None:
        return await self._collection.delete_many({})

    @staticmethod
    async def _clean_up():
        uris = [*MongoStore.__clients__.keys()]
        for uri in uris:
            MongoStore.__clients__[uri].close()
            del MongoStore.__clients__[uri]

    def __get_query(self, search_value: Any, is_regex: bool = False) -> Dict[str, Any]:
        """Constructs the filter query object for searching, getting or deleting"""
        if is_regex:
            query = {
                self._search_field: {"$regex": f"^{search_value}", "$options": "i"}
            }
        else:
            query = {self._search_field: search_value}

        if self._lang:
            query.update({"language": self._lang})

        return query

    def __register_client_if_not_exists(self, conf: Dict[str, Any]):
        """Registers the mongo client for the associated uri if it has not yet been registered"""
        if self.__uri not in MongoStore.__clients__:
            MongoStore.__clients__[self.__uri] = AsyncIOMotorClient(self.__uri, **conf)

    def __create_search_index_if_not_exists(self, conf: Dict[str, Any]):
        """Creates a unique index on the associated uri, database and collection"""
        sync_db = pymongo.MongoClient(self.__uri, **conf)

        try:
            keys = [(field, pymongo.ASCENDING) for field in self.__pk_fields]
            pk_fields_str = "_".join(self.__pk_fields)
            index_name = f"{self.__collection_name}_{pk_fields_str}"
            collection = sync_db[self.__database_name][self.__collection_name]

            collection.create_index(keys=keys, name=index_name, unique=True)
        finally:
            sync_db.close()
