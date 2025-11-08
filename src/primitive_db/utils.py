import json
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

TABLE_DATA_DIR = PROJECT_ROOT / "src" / "primitive_db" / "data"
METADATA_JSON = PROJECT_ROOT / "src" / "primitive_db" / "db_meta.json"


def load_metadata(filepath=METADATA_JSON):
    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("[]")
        return []

    if os.path.getsize(filepath) > 0:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    return []


def save_metadata(data, filepath=METADATA_JSON):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_table_path(table_name):
    return TABLE_DATA_DIR / f"{table_name}.json"


def load_table_data(table_name):
    filepath = get_table_path(table_name)
    if not filepath.exists():
        return {}

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_table_data(table_name, data):
    filepath = get_table_path(table_name)
    filepath.parent.mkdir(parents=True, exist_ok=True)  
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
