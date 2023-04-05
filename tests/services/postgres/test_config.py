import pytest

import tests.utils.shared
from services.store import PgStore

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
from ...utils.postgres import delete_pg_table, pg_table_exists


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
    accumulated_languages = [*tests.utils.shared.languages]
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
    songs_table = "songs"

    for lang in tests.utils.shared.languages:
        await delete_pg_table(db_path, songs_table)

        assert not await pg_table_exists(db_path, songs_table)
        store = get_titles_store(service_conf=conf, uri=db_path, lang=lang)
        assert isinstance(store, PgStore)
        assert store._search_field == "title"

        await store._create_table_if_not_created(force=True)
        assert await pg_table_exists(db_path, songs_table)


@pytest.mark.asyncio
@pytest.mark.parametrize("db_path, conf", service_configs_fixture)
async def test_get_numbers_store(db_path, conf):
    """get_numbers_store creates the songs table, with search field as number"""
    await save_service_config(db_path, conf)
    songs_table = "songs"

    for lang in tests.utils.shared.languages:
        await delete_pg_table(db_path, songs_table)

        assert not await pg_table_exists(db_path, songs_table)
        store = get_numbers_store(service_conf=conf, uri=db_path, lang=lang)
        assert isinstance(store, PgStore)
        assert store._search_field == "number"

        await store._create_table_if_not_created(force=True)
        assert await pg_table_exists(db_path, songs_table)
