import json
import os

from src.primitive_db import constants, decorators


@decorators.handle_db_errors
def load_metadata(filepath=constants.METADATA_JSON):
    """
    Загружает метаданные всех таблиц из файла db_meta.json.
    
    Если файл отсутствует — создаёт его и записывает пустой список.
    Если файл повреждён или содержит некорректный JSON — возвращает пустой список.
    
    Возвращает:
        list — список словарей с описанием таблиц.
    """
     
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


@decorators.handle_db_errors
def save_metadata(data, filepath=constants.METADATA_JSON):
    """
    Сохраняет актуальные метаданные таблиц в db_meta.json.
    
    Аргументы:
        data — структура метаданных (список словарей).
    """

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@decorators.handle_db_errors
def get_table_path(table_name):
    """
    Возвращает путь к JSON-файлу таблицы.
    
    Аргументы:
        table_name — имя таблицы.
        
    Возвращает:
        pathlib.Path — путь к файлу с данными таблицы.
    """

    return constants.TABLE_DATA_DIR / f'{table_name}.json'


@decorators.handle_db_errors
def load_table_data(table_name):
    """
    Загружает содержимое JSON-файла таблицы.
    
    Если файл отсутствует — возвращает пустой словарь.
    
    Аргументы:
        table_name — имя таблицы.
        
    Возвращает:
        dict — данные таблицы формата {column: list_of_values}.
    """

    filepath = get_table_path(table_name)
    if not filepath.exists():
        return {}

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


@decorators.handle_db_errors
def save_table_data(table_name, data):
    """
    Сохраняет данные таблицы в её JSON-файл.
    
    Если директории ещё нет — создаёт её.
    
    Аргументы:
        table_name — имя таблицы.
        data — словарь с данными таблицы.
    """
    
    filepath = get_table_path(table_name)
    filepath.parent.mkdir(parents=True, exist_ok=True)  
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
