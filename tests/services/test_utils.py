"""Tests for all utility functions common across services"""
import os

from services.utils import get_store_path


def test_get_store_path(root_folder_path):
    """Returns the path to the store given root path"""
    test_data = {
        "languages": os.path.join(root_folder_path, "languages"),
        "hymns": os.path.join(root_folder_path, "hymns"),
        "auth": os.path.join(root_folder_path, "auth"),
    }

    for k, v in test_data.items():
        assert get_store_path(root_folder_path, k) == v
