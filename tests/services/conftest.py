from pytest_lazyfixture import lazy_fixture
from services import hymns
from services.config import save_service_config
from tests.utils.mongo import is_mongo_titles_store, is_mongo_numbers_store
from tests.utils.postgres import is_pg_titles_store, is_pg_numbers_store

from tests.utils.shared import (
    aio_pytest_fixture,
    service_configs,
    songs,
    languages,
)

# For testing saving and getting config
configs_fixture = [
    (lazy_fixture("test_mongo_path"), conf) for conf in service_configs
] + [(lazy_fixture("test_pg_path"), conf) for conf in service_configs]

# For testing adding new languages
langs_fixture = [
    (lazy_fixture("test_mongo_path"), conf, languages) for conf in service_configs[:1]
] + [(lazy_fixture("test_pg_path"), conf, languages) for conf in service_configs[:1]]

# For testing creation of titles store
titles_stores_fixture = [
    (lazy_fixture("test_mongo_path"), conf, is_mongo_titles_store)
    for conf in service_configs
] + [
    (lazy_fixture("test_pg_path"), conf, is_pg_titles_store) for conf in service_configs
]

# For testing creation of numbers store
numbers_stores_fixture = [
    (lazy_fixture("test_mongo_path"), conf, is_mongo_numbers_store)
    for conf in service_configs
] + [
    (lazy_fixture("test_pg_path"), conf, is_pg_numbers_store)
    for conf in service_configs
]

# For testing initializing service
service_db_path_fixture = [
    lazy_fixture("mongo_service_db_path"),
    lazy_fixture("pg_service_db_path"),
]


# For testing CRUD for songs
songs_fixture = [(lazy_fixture("mongo_hymns_service"), song) for song in songs] + [
    (lazy_fixture("pg_hymns_service"), song) for song in songs
]


# For testing CRUD for songs requiring language specification
songs_langs_fixture = [
    (lazy_fixture("mongo_hymns_service"), song, languages) for song in songs
] + [(lazy_fixture("pg_hymns_service"), song, languages) for song in songs]

# For testing use of just the Hymns service
hymns_service_fixture = [
    lazy_fixture("mongo_hymns_service"),
    lazy_fixture("pg_hymns_service"),
]


@aio_pytest_fixture
async def mongo_service_db_path(test_mongo_path):
    """the mongo db path for the test service, after setting up configuration"""
    await save_service_config(test_mongo_path, service_configs[0])
    yield test_mongo_path


@aio_pytest_fixture
async def mongo_hymns_service(mongo_service_db_path):
    """the hymns service for use during tests when running on mongo db"""
    service = await hymns.initialize(mongo_service_db_path)
    yield service


@aio_pytest_fixture
async def pg_service_db_path(test_pg_path):
    """the postgres db path for the test service, after setting up configuration"""
    await save_service_config(test_pg_path, service_configs[0])
    yield test_pg_path


@aio_pytest_fixture
async def pg_hymns_service(pg_service_db_path):
    """the hymns service for use during tests  when running on postgres"""
    service = await hymns.initialize(pg_service_db_path)
    yield service
