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

_TEST_SERVICE_FOLDER = os.path.dirname(__file__)


@pytest.mark.asyncio
async def test_save_and_get_service_config():
    """save_service_config saves the config of the service in a database, get_service_config retrieves it"""
    root_path = os.path.join(_TEST_SERVICE_FOLDER, "test_db")
    _delete_folder(root_path)

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

    try:
        for expected in test_data:
            await save_service_config(root_path, expected)
            got = await get_service_config(root_path)
            assert got == expected
    finally:
        _delete_folder(root_path)


@pytest.mark.asyncio
async def test_add_new_language():
    """add_new_language adds a new language to the config"""
    root_path = os.path.join(_TEST_SERVICE_FOLDER, "test_db2")
    _delete_folder(root_path)

    test_data = ["Runyoro", "Lusamya", "Luganda", "Rukiga"]
    conf = ServiceConfig(
        max_keys=2_000,
        redundant_blocks=3,
        pool_capacity=4,
        compaction_interval=1800,
        languages=["English"],
    )
    accumulated_langs = [*conf.languages]

    try:
        await save_service_config(root_path, conf)

        for lang in test_data:
            await add_new_language(root_path, lang)
            saved_conf = await get_service_config(root_path)
            accumulated_langs.append(lang)
            assert saved_conf.languages == accumulated_langs
    finally:
        _delete_folder(root_path)


@pytest.mark.asyncio
async def test_get_titles_store():
    """get_titles_store gets the store for storing titles for a given language"""
    root_path = os.path.join(_TEST_SERVICE_FOLDER, "test_db3")
    _delete_folder(root_path)

    conf = ServiceConfig(
        max_keys=2_000,
        redundant_blocks=3,
        pool_capacity=4,
        compaction_interval=1800,
        languages=["Runyoro", "Lusamya", "Luganda", "Rukiga"],
    )

    try:
        await save_service_config(root_path, conf)

        for lang in conf.languages:
            titles_store_path = os.path.join(root_path, f"{lang}-title")
            _delete_folder(titles_store_path)

            assert not os.path.exists(titles_store_path)
            store = await get_titles_store(root_path, lang)
            assert isinstance(store, AsyncStore)
            assert os.path.exists(titles_store_path)
    finally:
        _delete_folder(root_path)


@pytest.mark.asyncio
async def test_get_numbers_store():
    """get_numbers_store gets the store for storing hymn numbers for a given language"""
    root_path = os.path.join(_TEST_SERVICE_FOLDER, "test_db4")
    _delete_folder(root_path)

    conf = ServiceConfig(
        max_keys=2_000,
        redundant_blocks=3,
        pool_capacity=4,
        compaction_interval=1800,
        languages=["Runyoro", "Lusamya", "Luganda", "Rukiga"],
    )

    try:
        await save_service_config(root_path, conf)

        for lang in conf.languages:
            numbers_store_path = os.path.join(root_path, f"{lang}-number")
            _delete_folder(numbers_store_path)

            assert not os.path.exists(numbers_store_path)
            store = await get_numbers_store(root_path, lang)
            assert isinstance(store, AsyncStore)
            assert os.path.exists(numbers_store_path)
    finally:
        _delete_folder(root_path)


def _delete_folder(path: str):
    """Deletes the folder at the given path"""
    shutil.rmtree(path=path, ignore_errors=True)
