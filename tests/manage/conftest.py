import os

from cryptography.fernet import Fernet
from pytest_lazyfixture import lazy_fixture
from typer.testing import CliRunner

from api.routes import app

from tests.utils.shared import setup_mail_config, aio_pytest_fixture

cli_runner_fixture = [
    (lazy_fixture("pg_cli_runner")),
    (lazy_fixture("mongo_cli_runner")),
]


@aio_pytest_fixture()
async def pg_cli_runner(test_pg_path):
    """the test client for the CLI part of the app"""
    _prepare_cli_env(test_pg_path)

    yield CliRunner()


@aio_pytest_fixture()
async def mongo_cli_runner(test_mongo_path):
    """the test client for the CLI part of the app"""
    _prepare_cli_env(test_mongo_path)

    yield CliRunner()


def _prepare_cli_env(db_path: str):
    """Prepares the environment for the CLI app

    Args:
        db_path: the path to the database
    """
    os.environ["APP_SETTINGS"] = "testing"
    os.environ["DB_PATH"] = db_path
    os.environ["API_SECRET"] = Fernet.generate_key().decode()
    os.environ["OTP_VERIFICATION_URL"] = app.url_path_for("verify_otp")
    setup_mail_config()
