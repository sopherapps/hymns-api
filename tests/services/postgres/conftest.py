from pytest_lazyfixture import lazy_fixture
from services import hymns
from services.config import save_service_config
from services.store import PgStore

from tests.utils import (
    aio_pytest_fixture,
    service_configs,
    songs,
    languages,
    drop_pg_db_if_exists,
    create_pg_db_if_not_exists,
)

service_configs_fixture = [
    (lazy_fixture("test_db_path"), conf) for conf in service_configs
]
service_configs_langs_fixture = [
    (lazy_fixture("test_db_path"), conf, languages) for conf in service_configs[:1]
]
songs_fixture = [(lazy_fixture("hymns_service"), song) for song in songs]
songs_langs_fixture = [
    (lazy_fixture("hymns_service"), song, languages) for song in songs
]


@aio_pytest_fixture
async def test_db_path():
    """the db path to the test db"""
    db_path = "postgresql://postgres@127.0.0.1:5432/test_db"
    await create_pg_db_if_not_exists(db_path)

    yield db_path
    await PgStore._clean_up()
    await drop_pg_db_if_exists(db_path)


@aio_pytest_fixture
async def service_db_path(test_db_path):
    """the root path for the test service, after setting up configuration"""
    await save_service_config(test_db_path, service_configs[0])
    yield test_db_path


@aio_pytest_fixture
async def hymns_service(service_db_path):
    """the hymns service for use during tests"""
    service = await hymns.initialize(service_db_path)
    yield service
