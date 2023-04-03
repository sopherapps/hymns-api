import os
from cryptography.fernet import Fernet
from pytest_lazyfixture import lazy_fixture
from starlette.testclient import TestClient

from api.routes import app

import pytest
from tests.utils import (
    setup_mail_config,
    delete_folder,
    languages,
    songs,
    rate_limits_per_second,
    get_rate_limit_string,
)

api_songs_langs_fixture = [
    (lazy_fixture("test_client"), song, languages) for song in songs
]


@pytest.fixture()
def test_client(root_folder_path):
    """the http test client for testing the API part of the project"""
    db_path = os.path.join(root_folder_path, "test_db")
    os.environ["DB_PATH"] = db_path
    os.environ["ENABLE_RATE_LIMIT"] = "False"
    os.environ["API_SECRET"] = Fernet.generate_key().decode()
    os.environ["OTP_VERIFICATION_URL"] = app.url_path_for("verify_otp")
    setup_mail_config()

    yield TestClient(app)
    delete_folder(db_path)


@pytest.fixture(params=rate_limits_per_second)
def test_client_and_rate_limit(root_folder_path, request):
    """Returns a rate limited test client for testing the API"""
    rate_limit = request.param
    db_path = os.path.join(root_folder_path, "test_db")
    os.environ["DB_PATH"] = db_path
    os.environ["RATE_LIMIT"] = get_rate_limit_string(rate_limit)
    os.environ["ENABLE_RATE_LIMIT"] = "True"
    os.environ["API_SECRET"] = Fernet.generate_key().decode()
    os.environ["OTP_VERIFICATION_URL"] = app.url_path_for("verify_otp")
    setup_mail_config()

    yield TestClient(app), rate_limit
    app.state.limiter.reset()
    delete_folder(db_path)
