import asyncio
import os

import funml as ml
from cryptography.fernet import Fernet
from pytest_lazyfixture import lazy_fixture
from fastapi.testclient import TestClient

from api.routes import app
from services import auth

from tests.utils import (
    setup_mail_config,
    languages,
    songs,
    get_rate_limit_string,
    rate_limits_per_second,
    aio_pytest_fixture,
    create_pg_user_table,
    pg_upsert_user,
)

api_songs_langs_fixture = [
    (lazy_fixture("test_client"), song, languages) for song in songs
]

test_user = auth.models.UserDTO(
    username="johndoe",
    email="johndoe@example.com",
    password="johnpassword",
)


@aio_pytest_fixture
async def test_client(test_pg_path):
    """the http test client for testing the API part of the project"""
    os.environ["DB_PATH"] = test_pg_path
    os.environ["ENABLE_RATE_LIMIT"] = "False"
    os.environ["API_SECRET"] = api_secret = Fernet.generate_key().decode()
    os.environ["OTP_VERIFICATION_URL"] = app.url_path_for("verify_otp")
    setup_mail_config()

    await create_pg_user_table(test_pg_path)
    await pg_upsert_user(test_pg_path, fernet=Fernet(api_secret), user=test_user)

    yield TestClient(app)


@aio_pytest_fixture(params=rate_limits_per_second)
async def test_client_and_rate_limit(test_pg_path, request):
    """Returns a rate limited test client for testing the API"""
    rate_limit = request.param
    os.environ["DB_PATH"] = test_pg_path
    os.environ["RATE_LIMIT"] = get_rate_limit_string(rate_limit)
    os.environ["ENABLE_RATE_LIMIT"] = "True"
    os.environ["API_SECRET"] = api_secret = Fernet.generate_key().decode()
    os.environ["OTP_VERIFICATION_URL"] = app.url_path_for("verify_otp")
    setup_mail_config()

    await create_pg_user_table(test_pg_path)
    await pg_upsert_user(test_pg_path, fernet=Fernet(api_secret), user=test_user)

    yield TestClient(app), rate_limit
    app.state.limiter.reset()
