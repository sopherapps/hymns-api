import os

# Path to the Database folder
from services.config import ServiceConfig

_default_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db")


def get_db_path() -> str:
    """Gets the db path for the app"""
    return os.getenv("DB_PATH", _default_db_path)


def get_hymns_service_config() -> ServiceConfig:
    """Gets the service config for the hymns service"""
    return ServiceConfig(
        max_keys=int(os.getenv("MAX_HYMNS", "2_000_000")),
        redundant_blocks=int(os.getenv("DB_REDUNDANCY_BLOCKS", "2")),
        pool_capacity=int(os.getenv("DB_BUFFER_POOL_CAPACITY", "5")),
        compaction_interval=int(os.getenv("DB_COMPACTION_INTERVAL", "3600")),
        languages=[
            lang.strip()
            for lang in os.getenv("LANGUAGES", "english,runyoro").split(",")
        ],
    )


# FastAPI
def get_api_key_length() -> int:
    """Gets the length of all API KEY's that will be generated"""
    return int(os.getenv("API_KEY_LENGTH", "32"))
