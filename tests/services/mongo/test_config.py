import pytest
from motor.motor_asyncio import AsyncIOMotorCollection

from services.store import MongoStore

from services.config import (
    save_service_config,
    get_service_config,
    add_new_language_in_place,
    get_titles_store,
    get_numbers_store,
)

from .conftest import (
    service_configs_fixture,
    service_configs_langs_fixture,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("db_path, expected", service_configs_fixture)
async def test_save_and_get_service_config(db_path, expected):
    """save_service_config saves the config of the service in a database, get_service_config retrieves it"""
    await save_service_config(db_path, expected)
    got = await get_service_config(db_path)
    assert got == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("db_path, conf, languages", service_configs_langs_fixture)
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
@pytest.mark.parametrize("db_path, conf", service_configs_fixture)
async def test_get_titles_store(db_path, conf):
    """get_titles_store creates the songs table, with search field as title"""
    await save_service_config(db_path, conf)

    for lang in conf.languages:
        store = get_titles_store(service_conf=conf, uri=db_path, lang=lang)
        assert isinstance(store, MongoStore)
        assert store._search_field == "title"
        assert store._lang == lang
        assert isinstance(store._collection, AsyncIOMotorCollection)
        assert store._collection.full_name == f"data.songs"


@pytest.mark.asyncio
@pytest.mark.parametrize("db_path, conf", service_configs_fixture)
async def test_get_numbers_store(db_path, conf):
    """get_numbers_store creates the songs table, with search field as number"""
    await save_service_config(db_path, conf)

    for lang in conf.languages:
        store = get_numbers_store(service_conf=conf, uri=db_path, lang=lang)
        assert isinstance(store, MongoStore)
        assert store._search_field == "number"
        assert store._lang == lang
        assert isinstance(store._collection, AsyncIOMotorCollection)
        assert store._collection.full_name == f"data.songs"
