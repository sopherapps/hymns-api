import os.path
import shutil

import pytest
from py_scdb import AsyncStore

from services.config import (
    save_service_config,
    ServiceConfig,
    get_service_config,
    add_new_language,
    get_titles_store,
    get_numbers_store,
)
from tests.conftest import delete_folder


@pytest.mark.asyncio
async def test_save_and_get_service_config(test_db_path):
    """save_service_config saves the config of the service in a database, get_service_config retrieves it"""
    test_data = [
        ServiceConfig(
            max_keys=1_000,
            redundant_blocks=1,
            pool_capacity=5,
            compaction_interval=3600,
            languages=["Lingala"],
        ),
        ServiceConfig(
            max_keys=2_000,
            redundant_blocks=3,
            pool_capacity=4,
            compaction_interval=1800,
            languages=["English"],
        ),
    ]

    for expected in test_data:
        await save_service_config(test_db_path, expected)
        got = await get_service_config(test_db_path)
        assert got == expected


@pytest.mark.asyncio
async def test_add_new_language(test_db_path):
    """add_new_language adds a new language to the config"""
    test_data = ["Runyoro", "Lusamya", "Luganda", "Rukiga"]
    conf = ServiceConfig(
        max_keys=2_000,
        redundant_blocks=3,
        pool_capacity=4,
        compaction_interval=1800,
        languages=["English"],
    )
    accumulated_langs = [*conf.languages]

    await save_service_config(test_db_path, conf)

    for lang in test_data:
        await add_new_language(test_db_path, lang)
        saved_conf = await get_service_config(test_db_path)
        accumulated_langs.append(lang)
        assert saved_conf.languages == accumulated_langs


@pytest.mark.asyncio
async def test_get_titles_store(test_db_path):
    """get_titles_store gets the store for storing titles for a given language"""
    conf = ServiceConfig(
        max_keys=2_000,
        redundant_blocks=3,
        pool_capacity=4,
        compaction_interval=1800,
        languages=["Runyoro", "Lusamya", "Luganda", "Rukiga"],
    )

    await save_service_config(test_db_path, conf)

    for lang in conf.languages:
        titles_store_path = os.path.join(test_db_path, f"{lang}-title")
        delete_folder(titles_store_path)

        assert not os.path.exists(titles_store_path)
        store = await get_titles_store(test_db_path, lang)
        assert isinstance(store, AsyncStore)
        assert os.path.exists(titles_store_path)


@pytest.mark.asyncio
async def test_get_numbers_store(test_db_path):
    """get_numbers_store gets the store for storing hymn numbers for a given language"""
    conf = ServiceConfig(
        max_keys=2_000,
        redundant_blocks=3,
        pool_capacity=4,
        compaction_interval=1800,
        languages=["Runyoro", "Lusamya", "Luganda", "Rukiga"],
    )

    await save_service_config(test_db_path, conf)

    for lang in conf.languages:
        numbers_store_path = os.path.join(test_db_path, f"{lang}-number")
        delete_folder(numbers_store_path)

        assert not os.path.exists(numbers_store_path)
        store = await get_numbers_store(test_db_path, lang)
        assert isinstance(store, AsyncStore)
        assert os.path.exists(numbers_store_path)
