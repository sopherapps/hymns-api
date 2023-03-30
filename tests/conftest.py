import os

import pytest

_ROOT_FOLDER_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture()
def root_folder_path():
    """the path to the root folder"""
    yield _ROOT_FOLDER_PATH
