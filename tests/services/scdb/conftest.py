import os
from pytest_lazyfixture import lazy_fixture
from services import hymns
from services.config import save_service_config

import pytest
from tests.utils import (
    delete_folder,
    aio_pytest_fixture,
    service_configs,
    songs,
    languages,
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


@pytest.fixture()
def test_db_path(root_folder_path):
    """the path to the test db"""
    db_path = os.path.join(root_folder_path, "test_db")
    yield db_path
    delete_folder(db_path)


@aio_pytest_fixture
async def service_root_path(test_db_path):
    """the root path for the test service, after setting up configuration"""
    await save_service_config(test_db_path, service_configs[0])
    yield test_db_path


@aio_pytest_fixture
async def hymns_service(service_root_path):
    """the hymns service for use during tests"""
    service = await hymns.initialize(service_root_path)
    yield service
