from pytest_lazyfixture import lazy_fixture
from services import hymns
from services.config import save_service_config

from tests.utils.shared import (
    aio_pytest_fixture,
    service_configs,
    songs,
    languages,
)

service_configs_fixture = [
    (lazy_fixture("test_mongo_path"), conf) for conf in service_configs
]
service_configs_langs_fixture = [
    (lazy_fixture("test_mongo_path"), conf, languages) for conf in service_configs[:1]
]
songs_fixture = [(lazy_fixture("hymns_service"), song) for song in songs]
songs_langs_fixture = [
    (lazy_fixture("hymns_service"), song, languages) for song in songs
]


@aio_pytest_fixture
async def service_db_path(test_mongo_path):
    """the root path for the test service, after setting up configuration"""
    await save_service_config(test_mongo_path, service_configs[0])
    yield test_mongo_path


@aio_pytest_fixture
async def hymns_service(service_db_path):
    """the hymns service for use during tests"""
    service = await hymns.initialize(service_db_path)
    yield service
