"""Tests for all utility functions common across services"""
import os


from services.utils import get_store_path, unit_expn

_ROOT_FOLDER_PATH = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


def test_get_store_path():
    """Returns the path to the store"""
    test_data = {
        "languages": os.path.join(_ROOT_FOLDER_PATH, "languages"),
        "hymns": os.path.join(_ROOT_FOLDER_PATH, "hymns"),
        "auth": os.path.join(_ROOT_FOLDER_PATH, "auth"),
    }

    for k, v in test_data.items():
        assert get_store_path(k) == v


def test_unit_expn():
    """Unit expression returns exactly what it is passed"""
    test_data = [None, 90, 90.8, "indigo", {"y": 90}]
    for data in test_data:
        assert unit_expn(data) == data
