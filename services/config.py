"""Handles the configuration of the entire app"""
from __future__ import annotations
import json
from typing import TYPE_CHECKING

from funml import to_dict
from py_scdb import AsyncStore
import funml as ml

from services.utils import get_store_path

if TYPE_CHECKING:
    from os import PathLike


_config_key = "config"  # The database key for service config


async def save_service_config(
    root_path: str | bytes | PathLike[bytes], conf: ServiceConfig
):
    """Saves service config.

    Args:
        root_path: the path to the root folder where the database is to be initialized or is found
        conf: the ServiceConfig object to save to the database
    """
    config_store = _get_config_store(root_path)
    key = _config_key
    value = ml.to_json(conf)
    await config_store.set(key, value)


async def get_service_config(
    root_path: str | bytes | PathLike[bytes],
) -> "ServiceConfig":
    """Retrieves the Service Config from the database at the given root_path.

    Args:
        root_path: the path to the root folder where the database is found

    Returns:
        the service config object found at the given path

    Raises:
        ValueError: no persistent service configuration as of yet
    """
    config_store = _get_config_store(root_path)
    config_as_str = await config_store.get(_config_key)

    if config_as_str is None:
        raise ValueError("no persistent service configuration as of yet")

    config_as_dict = json.loads(config_as_str)
    return ServiceConfig(**config_as_dict)


async def add_new_language(root_path: str | bytes | PathLike[bytes], lang: str):
    """Adds a new language to the service config, persisting it to file."""
    conf = await get_service_config(root_path)
    conf_as_dict = to_dict(conf)
    conf_as_dict["languages"] = [*conf.languages, lang]
    new_conf = ServiceConfig(**conf_as_dict)
    await save_service_config(root_path, conf=new_conf)


async def get_titles_store(root_path: str | bytes | PathLike[bytes], lang: str):
    """Gets the AsyncStore for hymns of the given language where the keys are titles"""
    conf = await _get_db_config(root_path, name=f"{lang}-title")
    conf_as_dict = to_dict(conf)
    return AsyncStore(**conf_as_dict)


async def get_numbers_store(root_path: str | bytes | PathLike[bytes], lang: str):
    """Gets the AsyncStore for hymns of the given language where the keys are numbers"""
    conf = await _get_db_config(root_path, name=f"{lang}-number")
    conf_as_dict = to_dict(conf)
    return AsyncStore(**conf_as_dict)


async def get_auth_store(root_path: str | bytes | PathLike[bytes]):
    """Gets the AsyncStore for the auth keys"""
    conf = await _get_db_config(root_path, name=f"hymns-auth")
    conf_as_dict = to_dict(conf)
    return AsyncStore(**conf_as_dict)


async def get_users_store(root_path: str | bytes | PathLike[bytes]):
    """Gets the AsyncStore for the users"""
    conf = await _get_db_config(root_path, name=f"hymns-users")
    conf_as_dict = to_dict(conf)
    return AsyncStore(**conf_as_dict)


async def _get_db_config(
    root_path: str | bytes | PathLike[bytes], name: str
) -> DbConfig:
    """Gets the DbConfig for a usual database given the name of the database"""
    store_path = get_store_path(root_path, name)
    service_conf = await get_service_config(root_path)
    return DbConfig(
        store_path=store_path,
        is_search_enabled=True,
        max_keys=service_conf.max_keys,
        redundant_blocks=service_conf.redundant_blocks,
        pool_capacity=service_conf.pool_capacity,
        compaction_interval=service_conf.compaction_interval,
    )


def _get_config_store(root_path: str | bytes | PathLike[bytes]) -> AsyncStore:
    """Gets the persistent store for the configuration of the service"""
    store_path = get_store_path(root_path, _config_key)
    conf = DbConfig(store_path=store_path)
    conf_as_dict = to_dict(conf)
    return AsyncStore(**conf_as_dict)


@ml.record
class ServiceConfig:
    """The configuration for the entire service"""

    # Db Config
    max_keys: int = 2_000_000
    redundant_blocks: int = 2
    pool_capacity: int = 5
    compaction_interval: int = 3600

    # General
    languages: list[str] = []


@ml.record
class DbConfig:
    store_path: str
    max_keys: int | None = 1000
    redundant_blocks: int | None = 1
    pool_capacity: int | None = 2
    compaction_interval: int | None = 3600
    is_search_enabled: bool = False
