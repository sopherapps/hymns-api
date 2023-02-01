"""Tests for all utility functions common across services"""
import os

from services.utils import get_store_path

_ROOT_FOLDER_PATH = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


def test_get_store_path():
    """Returns the path to the store"""
    test_data = {
        "languages": os.path.join(_ROOT_FOLDER_PATH, "languages-dump"),
        "hymns": os.path.join(_ROOT_FOLDER_PATH, "hymns-dump"),
        "auth": os.path.join(_ROOT_FOLDER_PATH, "auth-dump"),
    }

    for k, v in test_data.items():
        assert get_store_path(k) == v
