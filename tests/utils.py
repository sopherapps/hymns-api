"""Utilities for tests"""
import os
import shutil
import urllib
from urllib.parse import urlparse

import pytest
import pytest_asyncio
import asyncpg
from sqlalchemy import make_url

from services.config import ServiceConfig
from services.hymns.models import LineSection, Song
from services.types import MusicalNote

aio_pytest_fixture = getattr(pytest_asyncio, "fixture", pytest.fixture())


service_configs = [
    ServiceConfig(
        max_keys=1_000,
        redundant_blocks=1,
        pool_capacity=5,
        compaction_interval=3600,
        languages=["Lingala"],
    ),
    ServiceConfig(
        max_keys=2_000,
        redundant_blocks=3,
        pool_capacity=4,
        compaction_interval=1800,
        languages=["English"],
    ),
]
languages = ["Runyoro", "Lusamya", "Luganda", "Rukiga", "Sebei"]
songs = [
    Song(
        number=90,
        language="English",
        title="Foo",
        key=MusicalNote.C_MAJOR,
        lines=[
            [
                LineSection(note=MusicalNote.C_MAJOR, words="The song"),
                LineSection(note=MusicalNote.G_MAJOR, words="is starting"),
                LineSection(note=MusicalNote.A_MINOR, words="It really"),
                LineSection(note=MusicalNote.F_MAJOR, words="is starting"),
            ],
            [
                LineSection(note=MusicalNote.A_MINOR, words="Get up"),
                LineSection(note=MusicalNote.F_MAJOR, words="and praise the LORD"),
                LineSection(note=MusicalNote.A_MINOR, words="The song"),
                LineSection(note=MusicalNote.F_MAJOR, words="has began"),
            ],
            [
                LineSection(note=MusicalNote.C_MAJOR, words="Wooo"),
                LineSection(note=MusicalNote.G_MAJOR, words="hoooo"),
                LineSection(note=MusicalNote.A_MINOR, words="Wooo"),
                LineSection(note=MusicalNote.F_MAJOR, words="hoooo"),
            ],
        ],
    ),
    Song(
        number=900,
        language="English",
        title="Bar",
        key=MusicalNote.C_MAJOR,
        lines=[
            [
                LineSection(note=MusicalNote.C_MAJOR, words="The poem"),
                LineSection(note=MusicalNote.G_MAJOR, words="is starting"),
                LineSection(note=MusicalNote.A_MINOR, words="It really"),
                LineSection(note=MusicalNote.F_MAJOR, words="is starting"),
            ],
            [
                LineSection(note=MusicalNote.A_MINOR, words="Get up"),
                LineSection(note=MusicalNote.F_MAJOR, words="and praise the LORD"),
                LineSection(note=MusicalNote.A_MINOR, words="The poem"),
                LineSection(note=MusicalNote.F_MAJOR, words="has began"),
            ],
            [
                LineSection(note=MusicalNote.C_MAJOR, words="Wee"),
                LineSection(note=MusicalNote.G_MAJOR, words="hee"),
                LineSection(note=MusicalNote.A_MINOR, words="wee"),
                LineSection(note=MusicalNote.F_MAJOR, words="heeee"),
            ],
        ],
    ),
]


def delete_folder(path: str):
    """Deletes the folder at the given path"""
    shutil.rmtree(path=path, ignore_errors=True)


def setup_mail_config():
    """Sets up the configuration for the email server"""
    os.environ["MAIL_USERNAME"] = "hymns@example.com"
    os.environ["MAIL_PASSWORD"] = "some-passowrd"
    os.environ["MAIL_FROM"] = "hymns@example.com"
    os.environ["MAIL_PORT"] = "587"
    os.environ["MAIL_SERVER"] = "some-server"
    os.environ["MAIL_DEBUG"] = "1"
    os.environ["MAIL_SUPPRESS_SEND"] = "1"


async def create_pg_db_if_not_exists(db_uri: str):
    """Creates a postgres database if not exists

    Args:
        db_uri: the postgres database url to connect to
    """
    try:
        conn = await asyncpg.connect(dsn=db_uri)
        await conn.close()
    except asyncpg.InvalidCatalogNameError:
        # Database does not exist, create it.
        uri = make_url(db_uri)
        sys_conn = await asyncpg.connect(
            database="template1",
            user="postgres",
            host=uri.host,
        )

        try:
            await sys_conn.execute(
                f"CREATE DATABASE {uri.database} OWNER {uri.username}"
            )
        finally:
            await sys_conn.close()


async def drop_pg_db_if_exists(db_uri: str):
    """Creates a postgres database if not exists

    Args:
        db_uri: the postgres database url to connect to
    """
    uri = make_url(db_uri)
    sys_conn = await asyncpg.connect(
        database="template1",
        user="postgres",
        host=uri.host,
    )
    try:
        await sys_conn.execute(f"DROP DATABASE IF EXISTS {uri.database}")
    finally:
        await sys_conn.close()


async def delete_pg_table(db_uri: str, table: str):
    """Drops a given table if exists

    Args:
        db_uri: the postgres database url to connect to
        table: the table to delete
    """
    conn = await asyncpg.connect(db_uri)
    try:
        await conn.execute(f"DROP TABLE IF EXISTS {table}")
    finally:
        await conn.close()


async def pg_table_exists(db_uri: str, table: str) -> bool:
    """Checks to see a given postgres table exists

    Args:
        db_uri: the postgres database url to connect to
        table: the table to check for
    """
    conn = await asyncpg.connect(db_uri)
    try:
        exists = await conn.fetchval(
            f"""SELECT EXISTS (
                    SELECT FROM 
                        pg_tables
                    WHERE 
                        schemaname = 'public' AND 
                        tablename  = '{table}'
                    )
            """
        )
    finally:
        await conn.close()

    return exists
