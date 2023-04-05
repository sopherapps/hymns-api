"""CLI managing the application
"""
import asyncio

import typer

import cli

app = typer.Typer(pretty_exceptions_show_locals=False)


@app.command()
def create_account(
    username: str = typer.Option(...),
    email: str = typer.Option(...),
    password: str = typer.Option(...),
):
    """Creates a new admin account"""
    try:
        asyncio.run(
            cli.create_account(username=username, email=email, password=password)
        )
        typer.echo("user created successfully")
    finally:
        asyncio.run(cli.shutdown())


@app.command()
def delete_account(
    username: str = typer.Option(...), password: str = typer.Option(...)
):
    """Deletes the account whose username and password are given"""
    try:
        asyncio.run(cli.delete_account(username=username, password=password))
        typer.echo("user deleted successfully")
    finally:
        asyncio.run(cli.shutdown())


@app.command()
def change_password(
    username: str = typer.Option(...),
    old_password: str = typer.Option(...),
    new_password: str = typer.Option(...),
):
    """Changes the password of the account"""
    try:
        asyncio.run(
            cli.change_password(
                username=username, old_password=old_password, new_password=new_password
            )
        )
        typer.echo("password changed successfully")
    finally:
        asyncio.run(cli.shutdown())


def shutdown():
    """Gracefully shuts down the app"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(cli.shutdown())


if __name__ == "__main__":
    try:
        app()
    finally:
        shutdown()
