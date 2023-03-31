"""Utilities associated with sqlalchemy"""
import re

import sqlalchemy
from typing import List, Dict, Any

from sqlalchemy import BigInteger, ForeignKey, String, Integer, JSON, Enum, Column

from services.types import MusicalNote

_song_collection_name_regex = re.compile(r"\w+_(title|number)")

_collection_table_name_map = {
    "config": "configs",
    "hymns_auth": "apps",
    "hymns_users": "users",
}
_collection_search_field_map = {
    "config": "key",
    "hymns_auth": "key",
    "hymns_users": "username",
}

_table_name_columns_map = {
    "configs": [Column("key", String, primary_key=True), Column("data", JSON)],
    "apps": [Column("key", String, primary_key=True)],
    "users": [
        Column("username", String(255), primary_key=True),
        Column("email", String(255), nullable=False),  # encrypted
        Column("password", String(255), nullable=False),  # hashed
        Column("otp_counter", String(255)),  # encrypted
        Column("otp_secret", String(255)),  # encrypted
        Column("login_attempts", Integer, default=0),
    ],
    "songs": [
        Column("number", String(255), primary_key=True),
        Column("language", String(255), primary_key=True),
        Column("title", String(255), primary_key=True),
        Column("key", Enum(MusicalNote), nullable=False),
        Column("lines", JSON, nullable=False),  # List[List[LineSection]]
    ],
}

_table_fields_map = {
    field: [col.name for col in columns]
    for field, columns in _table_name_columns_map.items()
}

_table_dependency_map: Dict[str, List[str]] = {}


def get_table_name(collection_name: str) -> str:
    """Gets the sqlalchemy table name for a given collection name"""
    try:
        return _collection_table_name_map[collection_name]
    except KeyError as exp:
        if _song_collection_name_regex.match(collection_name):
            return "songs"
        raise exp


def get_table_columns(table_name: str) -> List[sqlalchemy.Column]:
    """Gets the set of sqlalchemy columns for a given table_name"""
    return _table_name_columns_map[table_name]


def get_dependent_tables(table_name: str) -> List[str]:
    """Gets the list of table names on which the given table depends"""
    return _table_dependency_map.get(table_name, [])


def get_search_field(name: str) -> str:
    """Gets the search field for a given collection name"""
    try:
        return _collection_search_field_map[name]
    except KeyError:
        res = _song_collection_name_regex.match(name)
        if res:
            return res.group(1)

        raise KeyError(f"search field for {name} does not exist")


def extract_data_for_table(table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts the data for a given table name from the given data"""
    fields = _table_fields_map[table_name]
    return {field: data.get(field, None) for field in fields}
