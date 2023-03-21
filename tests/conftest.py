import os
import shutil

import pytest
import pytest_asyncio
from cryptography.fernet import Fernet
from pytest_lazyfixture import lazy_fixture
from fastapi.testclient import TestClient

import api.models
from api.routes import app
from services import hymns
from services.config import ServiceConfig, save_service_config
from services.hymns.models import LineSection, Song, MusicalNote

aio_pytest_fixture = getattr(pytest_asyncio, "fixture", pytest.fixture())

_ROOT_FOLDER_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_service_configs = [
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
_songs = [
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
api_songs = [api.models.Song.from_hymns(song) for song in _songs]

_rate_limits_per_second = [2, 10, 5]


service_configs_fixture = [
    (lazy_fixture("test_db_path"), conf) for conf in _service_configs
]
service_configs_langs_fixture = [
    (lazy_fixture("test_db_path"), conf, languages) for conf in _service_configs[:1]
]
songs_fixture = [(lazy_fixture("hymns_service"), song) for song in _songs]
songs_langs_fixture = [
    (lazy_fixture("hymns_service"), song, languages) for song in _songs
]
api_songs_langs_fixture = [
    (lazy_fixture("test_client"), song, languages) for song in api_songs
]


@pytest.fixture()
def root_folder_path():
    """the path to the root folder"""
    yield _ROOT_FOLDER_PATH


@pytest.fixture()
def test_db_path(root_folder_path):
    """the path to the test db"""
    db_path = os.path.join(root_folder_path, "test_db")
    yield db_path
    delete_folder(db_path)


@pytest.fixture()
def test_client(root_folder_path):
    """the http test client for testing the API part of the project"""
    db_path = os.path.join(root_folder_path, "test_db")
    os.environ["DB_PATH"] = db_path
    os.environ["ENABLE_RATE_LIMIT"] = "False"
    os.environ["API_SECRET"] = Fernet.generate_key().decode()
    os.environ["OTP_VERIFICATION_URL"] = app.url_path_for("verify_otp")
    _setup_mail_config()

    yield TestClient(app)
    delete_folder(db_path)


@aio_pytest_fixture
async def service_root_path(test_db_path):
    """the root path for the test service, after setting up configuration"""
    await save_service_config(test_db_path, _service_configs[0])
    yield test_db_path


@aio_pytest_fixture
async def hymns_service(service_root_path):
    """the hymns service for use during tests"""
    service = await hymns.initialize(service_root_path)
    yield service


@pytest.fixture(params=_rate_limits_per_second)
def test_client_and_rate_limit(root_folder_path, request):
    """Returns a rate limited test client for testing the API"""
    rate_limit = request.param
    db_path = os.path.join(root_folder_path, "test_db")
    os.environ["DB_PATH"] = db_path
    os.environ["RATE_LIMIT"] = get_rate_limit_string(rate_limit)
    os.environ["ENABLE_RATE_LIMIT"] = "True"
    os.environ["API_SECRET"] = Fernet.generate_key().decode()
    os.environ["OTP_VERIFICATION_URL"] = app.url_path_for("verify_otp")
    _setup_mail_config()

    yield TestClient(app), rate_limit
    # del app.state.limiter
    app.state.limiter.reset()
    delete_folder(db_path)


def delete_folder(path: str):
    """Deletes the folder at the given path"""
    shutil.rmtree(path=path, ignore_errors=True)


def get_rate_limit_string(num_per_second: int) -> str:
    """Converts a number of requests per second to the string notation for the slowapi library"""
    return f"{num_per_second} per 1 second"


def _setup_mail_config():
    """Sets up the configuration for the email server"""
    os.environ["MAIL_USERNAME"] = "hymns@example.com"
    os.environ["MAIL_PASSWORD"] = "some-passowrd"
    os.environ["MAIL_FROM"] = "hymns@example.com"
    os.environ["MAIL_PORT"] = "587"
    os.environ["MAIL_SERVER"] = "some-server"
    os.environ["MAIL_DEBUG"] = "1"
    os.environ["MAIL_SUPPRESS_SEND"] = "1"
