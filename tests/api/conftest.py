import os
from typing import Optional

from cryptography.fernet import Fernet
from pytest_lazyfixture import lazy_fixture
from fastapi.testclient import TestClient

from api.routes import app
from services import auth
from tests.utils.postgres import create_pg_user_table, pg_upsert_user

from tests.utils.shared import (
    setup_mail_config,
    languages,
    songs,
    get_rate_limit_string,
    rate_limits_per_second,
    aio_pytest_fixture,
)
from tests.utils.mongo import mongo_upsert_user

base_url = "http://example.com"

# For testing routes that need songs and languages
api_songs_langs_fixture = [
    (lazy_fixture("mongo_test_client"), song, languages) for song in songs
] + [(lazy_fixture("pg_test_client"), song, languages) for song in songs]

# For testing using just plain api clients
test_clients_fixture = [
    lazy_fixture("mongo_test_client"),
    lazy_fixture("pg_test_client"),
]


# For testing rate limits
test_clients_rate_limits_fixture = [
    lazy_fixture("mongo_test_client_and_rate_limit"),
    lazy_fixture("pg_test_client_and_rate_limit"),
]


test_user = auth.models.UserDTO(
    username="johndoe",
    email="johndoe@example.com",
    password="johnpassword",
)


@aio_pytest_fixture
async def mongo_test_client(test_mongo_path):
    """the http test client for testing the API part of the project when running on mongodb"""
    api_secret = _prepare_api_env(test_mongo_path)
    mongo_upsert_user(test_mongo_path, fernet=Fernet(api_secret), user=test_user)
    yield TestClient(app, base_url=base_url)


@aio_pytest_fixture(params=rate_limits_per_second)
async def mongo_test_client_and_rate_limit(test_mongo_path, request):
    """Returns a rate limited test client for testing the API when running on mongodb"""
    rate_limit = request.param
    api_secret = _prepare_api_env(test_mongo_path, rate_limit)
    mongo_upsert_user(test_mongo_path, fernet=Fernet(api_secret), user=test_user)

    yield TestClient(app, base_url=base_url), rate_limit
    app.state.limiter.reset()


@aio_pytest_fixture
async def pg_test_client(test_pg_path):
    """the http test client for testing the API part of the project when running on postgres"""
    api_secret = _prepare_api_env(test_pg_path)

    await create_pg_user_table(test_pg_path)
    await pg_upsert_user(test_pg_path, fernet=Fernet(api_secret), user=test_user)

    yield TestClient(app, base_url=base_url)


@aio_pytest_fixture(params=rate_limits_per_second)
async def pg_test_client_and_rate_limit(test_pg_path, request):
    """Returns a rate limited test client for testing the API when running on postgres"""
    rate_limit = request.param
    api_secret = _prepare_api_env(test_pg_path, rate_limit)

    await create_pg_user_table(test_pg_path)
    await pg_upsert_user(test_pg_path, fernet=Fernet(api_secret), user=test_user)

    yield TestClient(app, base_url=base_url), rate_limit
    app.state.limiter.reset()


def _prepare_api_env(db_path: str, rate_limit: Optional[int] = None) -> str:
    """Prepares the environment for the API

    Args:
        db_path: the path to the database
        rate_limit: the maximum number of requests per second for a given IP

    Returns:
        the API secret used for encrypting stuff
    """
    os.environ["DB_PATH"] = db_path
    os.environ["API_SECRET"] = api_secret = Fernet.generate_key().decode()
    os.environ["OTP_VERIFICATION_URL"] = app.url_path_for("verify_otp")
    os.environ["ENABLE_RATE_LIMIT"] = "False"
    setup_mail_config()

    if rate_limit is not None:
        os.environ["RATE_LIMIT"] = get_rate_limit_string(rate_limit)
        os.environ["ENABLE_RATE_LIMIT"] = "True"

    return api_secret
