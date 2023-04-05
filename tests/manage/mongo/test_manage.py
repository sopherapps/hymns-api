import asyncio

import pytest
from typer.testing import CliRunner

from cli import shutdown
from cli.auth import login
from manage import app
from services.auth.errors import AuthenticationError


def test_create_account(pg_cli_runner: CliRunner):
    """Can create a new account"""
    username = "johndoe"
    password = "password123"

    assert not _user_exists(username, password)
    result = pg_cli_runner.invoke(
        app,
        [
            "create-account",
            "--username",
            username,
            "--email",
            "johndoe@example.com",
            "--password",
            password,
        ],
    )
    assert result.exit_code == 0
    assert "user created successfully" in result.stdout
    assert _user_exists(username, password)


def test_create_account_no_duplicate_account(pg_cli_runner: CliRunner):
    """Cannot create a duplicate account"""
    username = "johndoe"
    password = "password123"

    result = pg_cli_runner.invoke(
        app,
        [
            "create-account",
            "--username",
            username,
            "--email",
            "johndoe@example.com",
            "--password",
            password,
        ],
    )
    assert result.exit_code == 0

    result = pg_cli_runner.invoke(
        app,
        [
            "create-account",
            "--username",
            username,
            "--email",
            "jane@example.com",
            "--password",
            "anotherPassword",
        ],
    )
    assert result.exit_code != 0
    assert "user already exists" in str(result.exception)

    assert _user_exists(username, password)


def test_delete_account(pg_cli_runner: CliRunner):
    """Can delete an account"""
    username = "johndoe"
    password = "password123"

    pg_cli_runner.invoke(
        app,
        [
            "create-account",
            "--username",
            username,
            "--email",
            "johndoe@example.com",
            "--password",
            password,
        ],
    )
    assert _user_exists(username, password)

    result = pg_cli_runner.invoke(
        app, ["delete-account", "--username", username, "--password", "password123"]
    )
    assert result.exit_code == 0
    assert "user deleted successfully" in result.stdout
    assert not _user_exists(username, password)


def test_change_password(pg_cli_runner: CliRunner):
    """Can change the password of the user"""
    username = "johndoe"
    old_password = "password123"
    new_password = "anotherPassword4"

    pg_cli_runner.invoke(
        app,
        [
            "create-account",
            "--username",
            username,
            "--email",
            "johndoe@example.com",
            "--password",
            old_password,
        ],
    )
    assert _user_exists(username, old_password)

    result = pg_cli_runner.invoke(
        app,
        [
            "change-password",
            "--username",
            username,
            "--old-password",
            old_password,
            "--new-password",
            new_password,
        ],
    )
    assert result.exit_code == 0
    assert "password changed successfully" in result.stdout

    res = asyncio.run(_guarded_login(username=username, password=new_password))
    assert res is not None

    with pytest.raises(AuthenticationError):
        asyncio.run(_guarded_login(username=username, password=old_password))


def _user_exists(username: str, password: str) -> bool:
    """Checks that the user of the given username and password exists"""
    try:
        res = asyncio.run(_guarded_login(username=username, password=password))
        return res is not None
    except AuthenticationError:
        return False


async def _guarded_login(username: str, password: str):
    """Logs in and always shuts down the app after"""
    try:
        result = await login(username=username, password=password)
    finally:
        await shutdown()
    return result
