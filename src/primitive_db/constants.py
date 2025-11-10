from pathlib import Path

from src.primitive_db import decorators

SELECT_CACHE, SELECT_CACHE_STORE = decorators.create_cacher()

PROJECT_ROOT = Path(__file__).resolve().parents[2]

TABLE_DATA_DIR = PROJECT_ROOT / 'src' / 'primitive_db' / 'data'
METADATA_JSON = PROJECT_ROOT / 'src' / 'primitive_db' / 'db_meta.json'
