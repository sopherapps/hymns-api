"""Handles the configuration of the entire app"""
from __future__ import annotations
from typing import TYPE_CHECKING

import services
from services.store import Store
from services.utils import Config

if TYPE_CHECKING:
    from os import PathLike


_config_key = "config"  # The database key for service config


async def save_service_config(uri: str | bytes | PathLike[bytes], conf: ServiceConfig):
    """Saves service config.

    Args:
        uri: the path to the root folder where the database is to be initialized or is found
        conf: the ServiceConfig object to save to the database
    """
    config_store = _get_config_store(uri)
    await config_store.set(_config_key, conf)


async def get_service_config(
    uri: str | bytes | PathLike[bytes],
) -> "ServiceConfig":
    """Retrieves the Service Config from the database at the given uri.

    Args:
        uri: the path to the root folder where the database is found

    Returns:
        the service config object found at the given path

    Raises:
        ValueError: no persistent service configuration as of yet
    """
    config_store = _get_config_store(uri)
    conf = await config_store.get(_config_key)

    if conf is None:
        raise ValueError("no persistent service configuration as of yet")

    return conf


async def add_new_language_in_place(
    service_conf: ServiceConfig, uri: str | bytes | PathLike[bytes], lang: str
):
    """Adds a new language to the service config, persisting it to file.

    Note that this mutates the service config passed to it
    """
    service_conf.languages.append(lang)
    await save_service_config(uri, conf=service_conf)


def get_titles_store(
    service_conf: ServiceConfig, uri: str | bytes | PathLike[bytes], lang: str
):
    """Gets the Store for hymns of the given language where the keys are titles"""
    return Store.retrieve_store(
        uri=uri,
        name=f"{lang}_title",
        model=services.hymns.models.Song,
        options=service_conf,
    )


def get_numbers_store(
    service_conf: ServiceConfig, uri: str | bytes | PathLike[bytes], lang: str
):
    """Gets the Store for hymns of the given language where the keys are numbers"""
    return Store.retrieve_store(
        uri=uri,
        name=f"{lang}_number",
        model=services.hymns.models.Song,
        options=service_conf,
    )


def get_auth_store(service_conf: ServiceConfig, uri: str | bytes | PathLike[bytes]):
    """Gets the Store for the auth keys"""
    return Store.retrieve_store(
        uri=uri,
        name="hymns_auth",
        model=services.auth.models.Application,
        options=service_conf,
    )


def get_users_store(service_conf: ServiceConfig, uri: str | bytes | PathLike[bytes]):
    """Gets the Store for the users"""
    return Store.retrieve_store(
        uri=uri,
        name="hymns_users",
        model=services.auth.models.UserInDb,
        options=service_conf,
    )


def _get_config_store(uri: str | bytes | PathLike[bytes]) -> Store:
    """Gets the persistent store for the configuration of the service"""
    return Store.retrieve_store(
        uri=uri, name=_config_key, model=ServiceConfig, options=Config()
    )


class ServiceConfig(Config):
    """The configuration for the entire service"""

    # Db Config
    max_keys: int = 2_000_000
    redundant_blocks: int = 2
    pool_capacity: int = 5
    compaction_interval: int = 3600
    is_search_enabled: bool = True

    # General
    languages: list[str] = []
