"""Handles all authentication and authorization"""
from typing import Union

import funml as ml

from services.auth.types import AuthService, Application
from services.config import get_auth_store
from .utils import generate_random_key


async def initialize(root_path: Union[bytes, str], key_size: int) -> "AuthService":
    """Initializes the auth service given the root path to the configuration store.

    Args:
        root_path: the path to the stores for the hymns service
        key_size: the size of the API key to be used

    Returns:
        the HymnsService whose configuration is at the root_path
    """
    store = await get_auth_store(root_path)
    return AuthService(store=store, key_size=key_size)


async def register_app(service: AuthService) -> ml.Result:
    """Registers a new application with the auth service if its name does not exist already

    It saves the application with a hashed key in the store but returns the application
    with its original key.

    Args:
        service: the auth service where the application is registered

    Returns:
        the created application with its raw key

    Raises:
        Exception: failed to create unique application key
    """
    try:
        key = generate_random_key(service.key_size)
        _app = await service.store.get(key)

        if _app is not None:
            raise Exception(f"failed to create unique application key")

        await service.store.set(key, "")

        return ml.Result.OK(Application(key=key))
    except Exception as exp:
        return ml.Result.ERR(exp)


async def is_valid_api_key(service: AuthService, key: str) -> bool:
    """Checks the validity of the given api key.

    Args:
        service: the auth service where the key is to be validated from
        key: the api key to be validated

    Returns:
        true if key is valid else false
    """
    res = await service.store.get(key)
    return res is not None
