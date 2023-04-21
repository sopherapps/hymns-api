import os

import pytest

from services.store import PgStore, MongoStore
from tests.utils.mongo import clear_mongo_db
from tests.utils.postgres import drop_pg_db_if_exists, create_pg_db_if_not_exists
from tests.utils.shared import (
    aio_pytest_fixture,
)


@pytest.fixture
def app_settings():
    """Sets the app settings to testing mode"""
    os.environ["APP_SETTINGS"] = "testing"


@aio_pytest_fixture
async def test_pg_path(app_settings):
    """the db path to the test postgres db"""
    db_path = os.getenv(
        "TEST_PG_DATABASE_URI", "postgresql://postgres@127.0.0.1:5432/test_hymns_api_db"
    )
    await drop_pg_db_if_exists(db_path)
    await create_pg_db_if_not_exists(db_path)

    yield db_path
    await PgStore._clean_up()
    await drop_pg_db_if_exists(db_path)


@aio_pytest_fixture
async def test_mongo_path(app_settings):
    """the db path to the test mongo db"""
    db_path = os.getenv("TEST_MONGO_DATABASE_URI", "mongodb://localhost:27017")

    clear_mongo_db(db_path)
    yield db_path

    await MongoStore._clean_up()
    clear_mongo_db(db_path)
