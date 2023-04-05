import os
from cryptography.fernet import Fernet
from typer.testing import CliRunner

from api.routes import app
from cli import initialize as cli_initialize
from tests.utils.scdb import delete_folder

from tests.utils.shared import aio_pytest_fixture, setup_mail_config


@aio_pytest_fixture
async def cli_runner(root_folder_path):
    """the test client for the CLI part of the app"""
    db_path = os.path.join(root_folder_path, "test_db")
    os.environ["DB_PATH"] = db_path
    os.environ["API_SECRET"] = Fernet.generate_key().decode()
    os.environ["OTP_VERIFICATION_URL"] = app.url_path_for("verify_otp")
    setup_mail_config()
    await cli_initialize(force=True)

    yield CliRunner()
    delete_folder(db_path)
