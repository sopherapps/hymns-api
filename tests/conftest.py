import contextlib
import os

import filelock
import pytest

from services.store import PgStore
from tests.utils import (
    aio_pytest_fixture,
    create_pg_db_if_not_exists,
    drop_pg_db_if_exists,
)

_ROOT_FOLDER_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture()
def root_folder_path():
    """the path to the root folder"""
    yield _ROOT_FOLDER_PATH


@aio_pytest_fixture
async def test_pg_path():
    """the db path to the test postgres db"""
    db_path = os.getenv(
        "TEST_PG_DATABASE_URI", "postgresql://postgres@127.0.0.1:5432/test_db"
    )
    await create_pg_db_if_not_exists(db_path)

    yield db_path
    await PgStore._clean_up()
    await drop_pg_db_if_exists(db_path)
