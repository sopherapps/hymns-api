"""Storage in postgres"""
import dataclasses
from typing import TypeVar, Type, Optional, List, Dict, Any

import sqlalchemy
from pydantic import BaseModel
from sqlalchemy import MetaData, Table, select, RowMapping, delete
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.dialects.postgresql import insert as pg_insert

from services.store.base import Store
from services.store.utils.collections import get_store_language_and_pk_field
from services.store.utils.sqlachemy import (
    get_table_name,
    get_table_columns,
    get_dependent_tables,
    extract_data_for_table,
    conv_model_to_dict,
    conv_dict_to_model,
)
from services.store.utils.uri import get_pg_async_uri
from services.utils import Config

T = TypeVar("T", bound=BaseModel)


class PgConfig(Config):
    pass


@dataclasses.dataclass
class PgConnection:
    """An SQLAlchemy engine with its meta data"""

    engine: AsyncEngine
    metadata: MetaData
    tables: Dict[str, Table] = dataclasses.field(default_factory=dict)


class PgStore(Store[T]):
    """Storage class implemented using postgres"""

    __store_type__: str = "postgresql"
    __store_config_cls__: Type[Config] = PgConfig
    __engines__: Dict[str, PgConnection] = {}
    __initialized_tables__: Dict[str, bool] = {}

    def __init__(self, uri: str, name: str, model: Type[T], options: PgConfig):
        super().__init__(uri, name, model, options)

        table_name = get_table_name(name)
        self.__engine_options = options
        self.__uri = uri
        self.__table_name = table_name
        self.__full_tablename = f"{uri}/{table_name}"
        self.__lang, self._search_field = get_store_language_and_pk_field(name)

        PgStore.__register_engine_if_not_exists(uri, options)
        PgStore._add_table_if_not_exists(table_name, uri)

        self.__pk_fields = [
            col.name for col in self.__table.primary_key.columns.values()
        ]

    @property
    def __table(self):
        """The table associated with this store"""
        return PgStore.__engines__[self.__uri].tables[self.__table_name]

    @property
    def __engine(self):
        """The engine associated with this store"""
        return PgStore.__engines__[self.__uri].engine

    @property
    def __is_table_created(self):
        """Whether the table has been created already"""
        return self.__full_tablename in PgStore.__initialized_tables__

    async def set(self, k: str, v: T, **kwargs) -> None:
        try:
            return await self.__set(k, v, **kwargs)
        except RuntimeError:
            await self.__engine.dispose()
            return await self.__set(k, v, **kwargs)

    async def get(self, k: str) -> Optional[T]:
        try:
            return await self.__get(k)
        except RuntimeError:
            await self.__engine.dispose()
            return await self.__get(k)

    async def search(self, term: str, skip: int = 0, limit: int = 0) -> List[T]:
        try:
            return await self.__search(term, skip, limit)
        except RuntimeError:
            await self.__engine.dispose()
            return await self.__search(term, skip, limit)

    async def delete(self, k: str) -> List[T]:
        try:
            return await self.__delete(k)
        except RuntimeError:
            await self.__engine.dispose()
            return await self.__delete(k)

    async def clear(self) -> None:
        try:
            return await self.__clear()
        except RuntimeError:
            await self.__engine.dispose()
            return await self.__clear()

    async def __set(self, k: str, v: T, **kwargs) -> None:
        """Set the value `v` to be associated with key `k` in the database"""
        await self._create_table_if_not_created()

        table_name = self.__table.name
        v_as_dict = conv_model_to_dict(table_name, v)
        data = {**{field: k for field in self.__pk_fields}, **v_as_dict}
        cleaned_data = extract_data_for_table(self.__table.name, data)
        return await self.__upsert(cleaned_data)

    async def __get(self, k: str) -> Optional[T]:
        """Get the value associated with the key `k`"""
        await self._create_table_if_not_created()

        clauses = self.__get_filter_clauses(k)
        select_stmt = select(self.__table).filter(*clauses)

        async with self.__engine.connect() as conn:
            res = await conn.execute(select_stmt)
            data = res.mappings().fetchone()
            if isinstance(data, RowMapping):
                return conv_dict_to_model(
                    self.__table.name, model=self._model, data=data
                )

    async def __search(self, term: str, skip: int = 0, limit: int = 0) -> List[T]:
        """Searches for the values of keys which satisfy the given search `term`, given the skip and the limit"""
        await self._create_table_if_not_created()

        clauses = self.__get_filter_clauses(term, is_ilike=True)
        select_stmt = select(self.__table).filter(*clauses)
        if limit > 0:
            select_stmt = select_stmt.limit(limit)
        if skip > 0:
            select_stmt = select_stmt.offset(skip)

        async with self.__engine.connect() as conn:
            res = await conn.execute(select_stmt)
            data = res.mappings().fetchall()

        table_name = self.__table.name
        return [
            conv_dict_to_model(table_name, model=self._model, data=item)
            for item in data
        ]

    async def __delete(self, k: str) -> List[T]:
        """Deletes the key-value whose key is `k`"""
        await self._create_table_if_not_created()

        clauses = self.__get_filter_clauses(k)
        delete_stmt = (
            delete(self.__table).filter(*clauses).returning(*self.__table.c.values())
        )

        async with self.__engine.begin() as conn:
            res = await conn.execute(delete_stmt)
            data = res.mappings()

        table_name = self.__table.name
        return [
            conv_dict_to_model(table_name, model=self._model, data=item)
            for item in data
        ]

    async def __clear(self) -> None:
        """Clears all the data in this collection"""
        await self._create_table_if_not_created()

        async with self.__engine.begin() as conn:
            await conn.run_sync(self.__table.metadata.drop_all, conn, [self.__table])
            await conn.run_sync(self.__table.metadata.create_all, conn, [self.__table])

    async def __upsert(self, data: Dict[str, Any]):
        """Inserts the data into the table if not exist"""
        insert_stmt = (
            pg_insert(self.__table)
            .values(**data)
            .on_conflict_do_update(index_elements=self.__pk_fields, set_=data)
        )

        async with self.__engine.begin() as conn:
            await conn.execute(insert_stmt)

    def __get_filter_clauses(
        self, search_value: Any, is_ilike: bool = False
    ) -> List[bool]:
        """Constructs the filter clauses for searching, getting or deleting"""
        search_col = getattr(self.__table.c, self._search_field)

        if is_ilike:
            clauses = [search_col.istartswith(search_value)]
        else:
            clauses = [search_col == search_value]

        if self.__lang:
            clauses.append(self.__table.c.language == self.__lang)

        return clauses

    @staticmethod
    async def _clean_up():
        uris = [*PgStore.__engines__.keys()]
        for uri in uris:
            await PgStore.__engines__[uri].engine.dispose()
            del PgStore.__engines__[uri]

        PgStore.__initialized_tables__.clear()

    @staticmethod
    def _add_table_if_not_exists(table_name, uri):
        """Adds a new table to PgStore"""
        if table_name in PgStore.__engines__[uri].tables:
            return

        dependent_tables = get_dependent_tables(table_name)
        for name in dependent_tables:
            PgStore._add_table_if_not_exists(name, uri)

        columns = get_table_columns(table_name)
        table = Table(table_name, PgStore.__engines__[uri].metadata, *columns)
        PgStore.__engines__[uri].tables[table_name] = table

    async def _create_table_if_not_created(self, force=False):
        """Attempts to create the table in the database

        Args:
            force: if the creation should be done regardless
        """
        if not self.__is_table_created or force:
            async with self.__engine.begin() as conn:
                await conn.run_sync(
                    self.__table.metadata.create_all, tables=[self.__table]
                )

            PgStore.__initialized_tables__[self.__full_tablename] = True

    @staticmethod
    def __register_engine_if_not_exists(uri: str, options: PgConfig):
        """Registers the engine attached to this instance if has not yet been registered"""
        if uri not in PgStore.__engines__:
            conf = options.dict(exclude_none=True)
            engine = create_async_engine(get_pg_async_uri(uri), **conf)
            PgStore.__engines__[uri] = PgConnection(engine=engine, metadata=MetaData())
