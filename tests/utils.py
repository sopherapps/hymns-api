"""Utilities for tests"""
import os
import shutil

import pytest
import pytest_asyncio

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
