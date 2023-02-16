"""Tests for all utility functions common across services"""
import os

from services.utils import (
    get_store_path,
)

_ROOT_FOLDER_PATH = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


def test_get_store_path():
    """Returns the path to the store given root path"""
    test_data = {
        "languages": os.path.join(_ROOT_FOLDER_PATH, "languages"),
        "hymns": os.path.join(_ROOT_FOLDER_PATH, "hymns"),
        "auth": os.path.join(_ROOT_FOLDER_PATH, "auth"),
    }

    for k, v in test_data.items():
        assert get_store_path(_ROOT_FOLDER_PATH, k) == v


def test_record_to_json():
    """record_to_json converts a record to JSON string"""
    pass


def test_note_to_str():
    """note_to_str converts a MusicalNote into a string"""
    pass
