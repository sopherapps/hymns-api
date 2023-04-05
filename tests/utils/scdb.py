import os
import pathlib
import shutil

from services.store import ScdbStore, Store


def delete_folder(path: str):
    """Deletes the folder at the given path"""
    shutil.rmtree(path=path, ignore_errors=True)


async def is_scdb_titles_store(store: Store, lang: str):
    """Asserts that the scdb store passed is a titles store for given language"""
    assert isinstance(store, ScdbStore)
    assert store._lang == lang
    assert pathlib.Path(store._store_path).parts[-1] == f"{lang}_title"
    assert os.path.exists(store._store_path)


async def is_scdb_numbers_store(store: Store, lang: str):
    """Asserts that the scdb store passed is a numbers store for given language"""
    assert isinstance(store, ScdbStore)
    assert store._lang == lang
    assert pathlib.Path(store._store_path).parts[-1] == f"{lang}_number"
    assert os.path.exists(store._store_path)
