import os
import pathlib
import shutil

import py_scdb
import pyotp
from cryptography.fernet import Fernet

from services.auth.models import UserDTO, UserInDb
from services.auth.utils import encrypt_str, hash_password
from services.store import ScdbStore, Store


def delete_folder(path: str):
    """Deletes the folder at the given path"""
    shutil.rmtree(path=path, ignore_errors=True)


async def scdb_upsert_user(db_uri: str, fernet: Fernet, user: UserDTO):
    """Upsert a user into the scdb database at the database URI"""
    users_db_uri = os.path.join(db_uri, "hymns_users")
    store = py_scdb.AsyncStore(store_path=users_db_uri)
    data = UserInDb(
        username=f"{user.username}",
        email=f"{encrypt_str(fernet, user.email)}",
        password=f"{hash_password(user.password)}",
        otp_counter=f'{encrypt_str(fernet, "0")}',
        otp_secret=f"{encrypt_str(fernet, pyotp.random_base32())}",
        login_attempts=0,
    ).json()
    await store.set(user.username, data)


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
