import os

# Path to the Database folder
from services.config import ServiceConfig

_db_folder_name = os.getenv("DB_FOLDER", "db")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), _db_folder_name)

# hymns service Config
HYMNS_SERVICE_CONFIG = ServiceConfig(
    max_keys=2_000_000,
    redundant_blocks=2,
    pool_capacity=5,
    compaction_interval=3600,
    languages=["english", "runyoro"],
)
