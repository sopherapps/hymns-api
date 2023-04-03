"""Utilities associated with sqlalchemy"""
import json

from typing import List, Dict, Any, TypeVar, Type, Mapping

from pydantic import BaseModel
from sqlalchemy import String, Integer, JSON, Enum, Column

from services.hymns.models import LineSection
from services.store.utils.collections import song_collection_name_regex
from services.types import MusicalNote

T = TypeVar("T", bound=BaseModel)


class ColumnData:
    """Record to house the args and kwargs for creating a Column

    When Columns are reused for other tables, they raise an ArgumentError
    https://stackoverflow.com/questions/62801823/how-to-redefine-tables-with-the-same-name-in-sqlalchemy-using-classical-mapping/62846328#62846328
    So instead, we will redefine them each time, using the same arguments
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def to_column(self) -> Column:
        """Converts column data to Column"""
        return Column(*self.args, **self.kwargs)


_collection_table_name_map = {
    "config": "configs",
    "hymns_auth": "apps",
    "hymns_users": "users",
}

_table_name_columns_map: Dict[str, List[ColumnData]] = {
    "configs": [ColumnData("key", String, primary_key=True), ColumnData("data", JSON)],
    "apps": [ColumnData("key", String, primary_key=True)],
    "users": [
        ColumnData("username", String(255), primary_key=True),
        ColumnData("email", String(255), nullable=False),  # encrypted
        ColumnData("password", String(255), nullable=False),  # hashed
        ColumnData("otp_counter", String(255)),  # encrypted
        ColumnData("otp_secret", String(255)),  # encrypted
        ColumnData("login_attempts", Integer, default=0),
    ],
    "songs": [
        ColumnData("number", String(255), primary_key=True),
        ColumnData("language", String(255), primary_key=True),
        ColumnData("title", String(255), primary_key=True),
        ColumnData("key", Enum(MusicalNote), nullable=False),
        ColumnData("lines", JSON, nullable=False),  # List[List[LineSection]]
    ],
}

_table_fields_map = {
    field: [col.args[0] for col in columns]
    for field, columns in _table_name_columns_map.items()
}

_table_dependency_map: Dict[str, List[str]] = {}


def get_table_name(collection_name: str) -> str:
    """Gets the sqlalchemy table name for a given collection name"""
    try:
        return _collection_table_name_map[collection_name]
    except KeyError as exp:
        if song_collection_name_regex.match(collection_name):
            return "songs"
        raise exp


def get_table_columns(table_name: str) -> List[Column]:
    """Gets the set of sqlalchemy columns for a given table_name"""
    col_data_list = _table_name_columns_map[table_name]
    return [col_data.to_column() for col_data in col_data_list]


def get_dependent_tables(table_name: str) -> List[str]:
    """Gets the list of table names on which the given table depends"""
    return _table_dependency_map.get(table_name, [])


def conv_model_to_dict(table_name: str, data: BaseModel) -> Dict[str, Any]:
    """Converts the well-known models of the different collections into dictionaries

    Args:
        table_name: the sql table name for the given model
        data: the data to be converted into a dict

    Returns:
        a dictionary normalized to the data expected by the postgres table
    """
    if table_name == "configs":
        return dict(data=data.json())
    elif table_name == "songs":
        lines: List[List[LineSection]] = getattr(data, "lines", [])
        lines_of_dicts = [[section.dict() for section in line] for line in lines]

        number = f"{getattr(data, 'number')}"
        return {**data.dict(), "number": number, "lines": json.dumps(lines_of_dicts)}
    else:
        return data.dict()


def conv_dict_to_model(table_name: str, model: Type[T], data: Mapping[str, Any]) -> T:
    """Converts the mapping into the model given the table name

    Args:
        table_name: the sql table name for the given data
        model: the model type to convert to
        data: the mapping to be converted

    Returns:
        an instance of the model populated by the data
    """
    if table_name == "configs":
        kwargs = json.loads(data.get("data", "{}"))
        return model(**kwargs)
    elif table_name == "songs":
        kwargs = {**data, "lines": json.loads(data.get("lines", "[]"))}
        return model(**kwargs)
    else:
        return model(**data)


def extract_data_for_table(table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts the data for a given table name from the given data"""
    fields = _table_fields_map[table_name]
    return {field: data.get(field, None) for field in fields}
