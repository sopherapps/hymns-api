"""Utilities for collections"""
import re
from typing import Optional, Tuple

song_collection_name_regex = re.compile(r"(\w+)_(title|number)")
collection_search_field_map = {
    "config": "key",
    "hymns_auth": "key",
    "hymns_users": "username",
}


def get_store_language_and_pk_field(store_name: str) -> Tuple[Optional[str], str]:
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
