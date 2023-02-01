"""Handles the configuration of the entire app"""
import json
from collections import Awaitable
from dataclasses import asdict
from typing import Callable

from py_scdb import AsyncStore
from pydantic import BaseModel
import funml as ml

from services.utils import get_store_path, await_output

"""
Data Types
"""


@ml.record
class ServiceConfig(BaseModel):
    """The configuration for the entire service"""

    # Db Config
    max_keys: int = 2_000_000
    redundant_blocks: int = 2
    pool_capacity: int = 5
    compaction_interval: int = 3600

    # General
    languages: list[str] = []

    @property
    def lang_db_config(self):
        """the configuration specific to language dbs"""
        return dict(
            max_keys=self.max_keys,
            redundant_blocks=self.redundant_blocks,
            pool_capacity=self.pool_capacity,
            compaction_interval=self.compaction_interval,
        )


@ml.record
class DbConfig:
    store_path: str
    max_keys: int | None = None
    redundant_blocks: int | None = None
    pool_capacity: int | None = None
    compaction_interval: int | None = None
    is_search_enabled: bool = False


"""
Data
"""
_service_db_config = DbConfig(
    store_path=get_store_path("config"),
    max_keys=1000,
    redundant_blocks=1,
    pool_capacity=2,
    compaction_interval=3600,
    is_search_enabled=False,
)
"""The configuration for the db that keeps the service config"""

_config_key = "config"
"""The database key for service config"""


"""
Primitive Expressions
"""
_async_store_from_dict = ml.val(
    lambda v: AsyncStore(**v)
)  # type: Callable[[dict], AsyncStore]
"""Gets AsyncStore given a dictionary of arguments"""


_get_db_config = lambda name: DbConfig(
    store_path=get_store_path(name),
    is_search_enabled=True,
    **_service_db_config.lang_db_config,
)  # type: Callable[[str], DbConfig]
"""Gets the DbConfig for a usual database given the name of the database"""


_get_config_store = (
    lambda: ml.val(_service_db_config)
    >> asdict
    >> _async_store_from_dict
    >> ml.execute()
)  # type: Callable[[], AsyncStore]
"""Gets the persistent store for the configuration of the service"""


"""
Main Expressions
"""
save_service_config = lambda conf: _get_config_store().set(
    _config_key, conf.json()
)  # type: Callable[[ServiceConfig], Awaitable[None]]
"""Saves service config"""


get_service_config = (
    lambda: ml.val(_config_key)
    >> _get_config_store().get
    >> await_output
    >> json.loads
    >> (lambda v: ServiceConfig(**v))
    >> ml.execute()
)  # type: Callable[[], ServiceConfig]
"""Retrieves the Service Config"""


_append_lang_on_service_config = lambda lang: lambda conf: ServiceConfig(
    **conf.dict(), languages=[*conf.languages, lang]
)  # type: Callable[[ServiceConfig, str], Callable[[ServiceConfig], ServiceConfig]]
"""Immutably appends a language to the languages of the service config"""


add_new_language = (
    lambda lang: ml.val(get_service_config())
    >> _append_lang_on_service_config(lang)
    >> save_service_config
    >> ml.execute()
)  # type: Callable[[str], Awaitable[None]]
"""Adds a new language to the service config, persisting it to file."""


get_titles_store = lambda lang: (
    ml.val(f"{lang}-title")
    >> _get_db_config
    >> asdict
    >> _async_store_from_dict
    >> ml.execute()
)  # type: Callable[[str], AsyncStore]
"""Gets the AsyncStore for the given language where the key is the title"""


get_numbers_store = lambda lang: (
    ml.val(f"{lang}-number")
    >> _get_db_config
    >> asdict
    >> _async_store_from_dict
    >> ml.execute()
)  # type: Callable[[str], AsyncStore]
"""Gets the AsyncStore for the given language where the key is the number"""
