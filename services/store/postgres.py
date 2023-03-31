"""Storage in postgres"""
import dataclasses
from typing import TypeVar, Type, Optional, List, Dict, Any

from pydantic import BaseModel
from sqlalchemy import MetaData, Table, select, RowMapping, delete
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.dialects.postgresql import insert as pg_insert

from services.store.base import Store
from services.store.utils.sqlachemy import (
    get_table_name,
    get_table_columns,
    get_dependent_tables,
    extract_data_for_table,
    get_search_field,
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


class PgStore(Store):
    """Storage class implemented using postgres"""

    __store_type__: str = "postgresql"
    __store_config_cls__: Type[Config] = PgConfig
    __engines__: Dict[str, PgConnection] = {}
    __is_initialized__: bool = False

    def __init__(self, uri: str, name: str, options: PgConfig):
        super().__init__(uri, name, options)

        if uri not in PgStore.__engines__:
            conf = options.dict(exclude_none=True)
            engine = create_async_engine(get_pg_async_uri(uri), **conf)
            PgStore.__engines__[uri] = PgConnection(engine=engine, metadata=MetaData())

        table_name = get_table_name(name)
        PgStore._add_table_if_not_exists(table_name, uri)

        self.__table = PgStore.__engines__[uri].tables[table_name]
        self.__engine = PgStore.__engines__[uri].engine
        self.__pk_fields = [col.name for col in self.__table.primary_key()]
        self.__search_field = get_search_field(name)

    async def set(self, k: str, v: BaseModel, **kwargs) -> None:
        data = {**{field: k for field in self.__pk_fields}, **v.dict()}
        cleaned_data = extract_data_for_table(self.__table.name, data)
        return await self._upsert(cleaned_data)

    async def get(self, model: Type[T], k: str) -> Optional[T]:
        select_stmt = select(self.__table).filter(
            getattr(self.__table.c, self.__search_field) == k
        )

        async with self.__engine.connect() as conn:
            res = await conn.execute(select_stmt)
            data = res.mappings().fetchone()
            if isinstance(data, RowMapping):
                return model(**data)

    async def search(
        self, model: Type[T], term: str, skip: int = 0, limit: int = 0
    ) -> List[T]:
        select_stmt = select(self.__table).filter(
            getattr(self.__table.c, self.__search_field).ilike(term)
        )
        if limit > 0:
            select_stmt = select_stmt.limit(limit)
        if skip > 0:
            select_stmt = select_stmt.offset(skip)

        async with self.__engine.connect() as conn:
            res = await conn.execute(select_stmt)
            data = res.mappings().fetchall()
            return [model(**item) for item in data]

    async def delete(self, k: str) -> None:
        delete_stmt = delete(self.__table).filter(
            getattr(self.__table.c, self.__search_field) == k
        )

        async with self.__engine.connect() as conn:
            await conn.execute(delete_stmt)

    async def clear(self) -> None:
        async with self.__engine.connect() as conn:
            await conn.run_sync(self.__table.metadata.drop_all, conn, [self.__table])
            await conn.run_sync(self.__table.metadata.create_all, conn, [self.__table])

    async def _upsert(self, data: Dict[str, Any]):
        """Inserts the data into the table if not exist"""
        insert_stmt = (
            pg_insert(self.__table)
            .values(**data)
            .on_conflict_do_update(index_elements=self.__pk_fields)
        )

        async with self.__engine.connect() as conn:
            await conn.execute(insert_stmt)

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

    @staticmethod
    async def _clean_up():
        uris = [*PgStore.__engines__.keys()]
        for uri in uris:
            await PgStore.__engines__[uri].engine.dispose()
            del PgStore.__engines__[uri]

    @staticmethod
    async def _initialize_store():
        if not PgStore.__is_initialized__:
            for _, pg_conn in PgStore.__engines__.items():
                async with pg_conn.engine.connect() as conn:
                    await conn.run_sync(pg_conn.metadata.create_all)

            PgStore.__is_initialized__ = True
