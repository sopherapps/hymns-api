import pytest

import tests.utils.shared

from services.config import (
    save_service_config,
    get_service_config,
    add_new_language_in_place,
    get_titles_store,
    get_numbers_store,
)

from .conftest import (
    configs_fixture,
    titles_stores_fixture,
    numbers_stores_fixture,
    langs_fixture,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("db_path, expected", configs_fixture)
async def test_save_and_get_service_config(db_path, expected):
    """save_service_config saves the config of the service in a database, get_service_config retrieves it"""
    await save_service_config(db_path, expected)
    got = await get_service_config(db_path)
    assert got == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("db_path, conf, languages", langs_fixture)
async def test_add_new_language(db_path, conf, languages):
    """add_new_language adds a new language to the config"""
    accumulated_languages = [*conf.languages]
    await save_service_config(db_path, conf)

    for lang in languages:
        await add_new_language_in_place(service_conf=conf, uri=db_path, lang=lang)
        saved_conf = await get_service_config(db_path)
        accumulated_languages.append(lang)
        try:
            assert saved_conf.languages == accumulated_languages
        except AssertionError as exp:
            raise AssertionError(
                f"{exp}, saved_conf: {saved_conf}, langs: {accumulated_languages}"
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "db_path, conf, is_titles_store_for_lang", titles_stores_fixture
)
async def test_get_titles_store(db_path, conf, is_titles_store_for_lang):
    """get_titles_store creates the songs table, with search field as title"""
    await save_service_config(db_path, conf)

    for lang in tests.utils.shared.languages:
        store = get_titles_store(service_conf=conf, uri=db_path, lang=lang)
        await is_titles_store_for_lang(store, lang)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "db_path, conf, is_numbers_store_for_lang", numbers_stores_fixture
)
async def test_get_numbers_store(db_path, conf, is_numbers_store_for_lang):
    """get_numbers_store creates the songs table, with search field as number"""
    await save_service_config(db_path, conf)

    for lang in tests.utils.shared.languages:
        store = get_numbers_store(service_conf=conf, uri=db_path, lang=lang)
        await is_numbers_store_for_lang(store, lang)
