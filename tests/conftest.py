import os
import shutil

import pytest

_ROOT_FOLDER_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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


def delete_folder(path: str):
    """Deletes the folder at the given path"""
    shutil.rmtree(path=path, ignore_errors=True)
