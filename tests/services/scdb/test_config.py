import os.path

import pytest

import tests.utils.shared
from services.store.base import Store

from services.config import (
    save_service_config,
    get_service_config,
    add_new_language_in_place,
    get_titles_store,
    get_numbers_store,
)

from tests.services.scdb.conftest import (
    service_configs_fixture,
    service_configs_langs_fixture,
    delete_folder,
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
    accumulated_languages = [*tests.utils.shared.languages]
    await save_service_config(root_path, conf)

    for lang in languages:
        await add_new_language_in_place(service_conf=conf, uri=root_path, lang=lang)
        saved_conf = await get_service_config(root_path)
        accumulated_languages.append(lang)
        try:
            assert saved_conf.languages == accumulated_languages
        except AssertionError as exp:
            raise AssertionError(
                f"{exp}, saved_conf: {saved_conf}, langs: {accumulated_languages}"
            )


@pytest.mark.asyncio
@pytest.mark.parametrize("root_path, conf, languages", service_configs_langs_fixture)
async def test_get_titles_store(root_path, conf, languages):
    """get_titles_store gets the store for storing titles for a given language"""
    tests.utils.shared.languages = languages
    await save_service_config(root_path, conf)

    for lang in tests.utils.shared.languages:
        titles_store_path = os.path.join(root_path, f"{lang}_title")
        delete_folder(titles_store_path)

        assert not os.path.exists(titles_store_path)
        store = get_titles_store(service_conf=conf, uri=root_path, lang=lang)
        assert isinstance(store, Store)
        assert os.path.exists(titles_store_path)


@pytest.mark.asyncio
@pytest.mark.parametrize("root_path, conf, languages", service_configs_langs_fixture)
async def test_get_numbers_store(root_path, conf, languages):
    """get_numbers_store gets the store for storing hymn numbers for a given language"""
    tests.utils.shared.languages = languages
    await save_service_config(root_path, conf)

    for lang in tests.utils.shared.languages:
        numbers_store_path = os.path.join(root_path, f"{lang}_number")
        delete_folder(numbers_store_path)

        assert not os.path.exists(numbers_store_path)
        store = get_numbers_store(service_conf=conf, uri=root_path, lang=lang)
        assert isinstance(store, Store)
        assert os.path.exists(numbers_store_path)
