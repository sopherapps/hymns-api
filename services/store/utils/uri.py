"""Utilities related to store URIs"""


def get_store_type(uri: str) -> str:
    """Gets the store type from the uri given"""
    parts = uri.split("://")
    if len(parts) > 1:
        return parts[0]
    return "scdb"


def get_pg_async_uri(uri: str) -> str:
    """Returns the URI for postgres db that works with async"""
    return uri.replace("postgresql", "postgresql+asyncpg", 1)
