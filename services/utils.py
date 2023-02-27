"""Contains the utility functions shared across services"""
from __future__ import annotations

from os import path


from os import PathLike


def get_store_path(root_path: bytes | PathLike[bytes] | str, name: str) -> str:
    """Gets the path to the store given a root path"""
    return path.join(root_path, name)
