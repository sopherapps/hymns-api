"""Common utility functions for the store package"""


def get_store_type(uri: str) -> str:
    """Gets the store type from the uri given"""
    parts = uri.split("://")
    if len(parts) > 1:
        return parts[0]
    return "scdb"
