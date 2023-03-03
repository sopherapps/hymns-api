import os.path
import shutil

import pytest
from py_scdb import AsyncStore

from services.config import (
    save_service_config,
    get_service_config,
    add_new_language,
    get_titles_store,
    get_numbers_store,
)
from tests.conftest import (
    delete_folder,
    service_configs_fixture,
    service_configs_langs_fixture,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("root_path, expected", service_configs_fixture)
async def test_save_and_get_service_config(root_path, expected):
    """save_service_config saves the config of the service in a database, get_service_config retrieves it"""
    await save_service_config(root_path, expected)
    got = await get_service_config(root_path)
    assert got == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("root_path, conf, languages", service_configs_langs_fixture)
async def test_add_new_language(root_path, conf, languages):
    """add_new_language adds a new language to the config"""
    accumulated_languages = [*conf.languages]
    await save_service_config(root_path, conf)

    for lang in languages:
        await add_new_language(root_path, lang)
        saved_conf = await get_service_config(root_path)
        accumulated_languages.append(lang)
        assert saved_conf.languages == accumulated_languages


@pytest.mark.asyncio
@pytest.mark.parametrize("root_path, conf, languages", service_configs_langs_fixture)
async def test_get_titles_store(root_path, conf, languages):
    """get_titles_store gets the store for storing titles for a given language"""
    conf.languages = languages
    await save_service_config(root_path, conf)

    for lang in conf.languages:
        titles_store_path = os.path.join(root_path, f"{lang}-title")
        delete_folder(titles_store_path)

        assert not os.path.exists(titles_store_path)
        store = await get_titles_store(root_path, lang)
        assert isinstance(store, AsyncStore)
        assert os.path.exists(titles_store_path)


@pytest.mark.asyncio
@pytest.mark.parametrize("root_path, conf, languages", service_configs_langs_fixture)
async def test_get_numbers_store(root_path, conf, languages):
    """get_numbers_store gets the store for storing hymn numbers for a given language"""
    conf.languages = languages
    await save_service_config(root_path, conf)

    for lang in conf.languages:
        numbers_store_path = os.path.join(root_path, f"{lang}-number")
        delete_folder(numbers_store_path)

        assert not os.path.exists(numbers_store_path)
        store = await get_numbers_store(root_path, lang)
        assert isinstance(store, AsyncStore)
        assert os.path.exists(numbers_store_path)
