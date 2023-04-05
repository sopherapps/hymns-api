import os

from cryptography.fernet import Fernet
from typer.testing import CliRunner

from api.routes import app

from tests.utils.shared import setup_mail_config, aio_pytest_fixture


@aio_pytest_fixture()
async def pg_cli_runner(test_pg_path):
    """the test client for the CLI part of the app"""
    os.environ["APP_SETTINGS"] = "test"
    os.environ["DB_PATH"] = test_pg_path
    os.environ["API_SECRET"] = Fernet.generate_key().decode()
    os.environ["OTP_VERIFICATION_URL"] = app.url_path_for("verify_otp")
    setup_mail_config()

    yield CliRunner()
