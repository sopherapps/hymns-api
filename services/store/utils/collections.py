"""Utilities for collections"""
import re
from typing import Optional, Tuple, List, Dict

song_collection_name_regex = re.compile(r"(\w+)_(title|number)")
collection_search_field_map = {
    "config": "key",
    "hymns_auth": "key",
    "hymns_users": "username",
}
_collection_table_name_map = {
    "config": "configs",
    "hymns_auth": "apps",
    "hymns_users": "users",
}
_table_dependency_map: Dict[str, List[str]] = {}
_table_pk_field_map: Dict[str, List[str]] = {
    "configs": ["key"],
    "apps": ["key"],
    "users": ["username"],
    "songs": ["number", "title", "language"],
}


def get_store_language_and_search_field(store_name: str) -> Tuple[Optional[str], str]:
    """Gets the language of the store if the store is for songs, and the primary key field

    Args:
        store_name: name of the store

    Returns:
        song_language: the song language or None if the store name is not of a song store
        pk_field: the primary key field to use for searching, deleting, getting for records
    """
    song_regex_match = song_collection_name_regex.match(store_name)
    if song_regex_match:
        return song_regex_match.group(1), song_regex_match.group(2)
    return None, collection_search_field_map[store_name]


def get_table_name(collection_name: str) -> str:
    """Gets the sqlalchemy table name for a given collection name"""
    try:
        return _collection_table_name_map[collection_name]
    except KeyError as exp:
        if song_collection_name_regex.match(collection_name):
            return "songs"
        raise exp


def get_pk_fields(table_name: str) -> List[str]:
    """Gets the primary key fields for a given table_name"""
    return _table_pk_field_map.get(table_name, [])
