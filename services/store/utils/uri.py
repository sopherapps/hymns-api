"""Utilities related to store URIs"""
from urllib.parse import quote_plus

from sqlalchemy import make_url


def get_store_type(uri: str) -> str:
    """Gets the store type from the uri given"""
    parts = uri.split("://")
    if len(parts) > 1:
        return parts[0]
    raise ValueError(f"uri format '{uri}' not supported")


def escape_db_uri(uri: str) -> str:
    """Properly escapes the uri of the database"""
    parsed_uri = make_url(uri)
    user_details = ""
    if parsed_uri.username:
        user_details = f"{quote_plus(parsed_uri.username)}"
    if parsed_uri.password:
        user_details = f"{user_details}:{quote_plus(parsed_uri.password)}"

    database = "" if parsed_uri.database is None else f"/{parsed_uri.database}"
    port = "" if parsed_uri.port is None else f":{parsed_uri.port}"

    if user_details:
        return f"{parsed_uri.drivername}://{user_details}@{parsed_uri.host}{port}{database}"

    return f"{parsed_uri.drivername}://{parsed_uri.host}{port}{database}"


def get_pg_async_uri(uri: str) -> str:
    """Returns the URI for postgres db that works with async"""
    return uri.replace("postgresql", "postgresql+asyncpg", 1)
