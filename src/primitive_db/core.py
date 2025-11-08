from src.primitive_db import utils
from prettytable import PrettyTable
import os


def create_table(metadata, table_name, columns):
    # допустимые типы
    if not all(t in ('int', 'str', 'bool') for t in columns.values()):
        print('Недопустимые типы данных. Можно использовать только int, bool, str.')
        return
    
    # проверка на существование таблицы
    if metadata and any(table['table_name'] == table_name for table in metadata):
        print('Такая таблица уже существует.')
        return

    # если нет ID, добавляем автоматически
    if 'id' not in (name.lower() for name in columns.keys()):
        columns = {'id': 'int', **columns}

    # создаём запись
    metadata.append({
        'table_name': table_name,
        'columns': columns
    })
    print(f'Таблица {table_name} успешно создана.')

    # создаем json структуру файла таблицы
    new_table = {'table_name': table_name}
    for column_name in list(columns.keys()):
        new_table[column_name] = []
    utils.save_table_data(table_name, new_table)


def drop_table(metadata, table_name):
    for i, table in enumerate(metadata):
        if table['table_name'] == table_name:
            del metadata[i]
            table_path = utils.get_table_path(table_name)
            if os.path.exists(table_path):
                os.remove(table_path)
            print(f'Таблица {table_name} удалена.')
            return
    print('Такой таблицы не существует.')


def clean_values(values):
    cleaned_raw = []
    for value in values:
        value = value.strip()

        if value.startswith("("):
            value = value[1:]
        if value.endswith(")") or value.endswith(","):
            value = value[:-1]

        cleaned_raw.append(value)

    def convert(value):
        v = value.strip()
        if v.lower() == "true":
            return True
        if v.lower() == "false":
            return False
        if v.isdigit():
            return int(v)
        try:
            return float(v)
        except ValueError:
            return v  
    
    values_cleaned = tuple(convert(v) for v in cleaned_raw)
    return values_cleaned


def insert(metadata, table_name, values):
    values = clean_values(values)

    # проверка на существование таблицы
    if metadata and any(table['table_name'] == table_name for table in metadata):
        table_to_insert = utils.load_table_data(table_name)
        if not table_to_insert:
            print('Произошла ошибка, попробуйте снова')
            return
    else:
        print('Такой таблицы не существует.')
        
    # проверка на длину значений
    values_len = len(values)
    input_with_id = False
    if values_len == len(table_to_insert) - 1:
        input_with_id = True
    if not input_with_id and values_len != len(table_to_insert) - 2:
        print('Неправильное число значений. ' + \
              f'Таблица {table_name} содержит {len(table_to_insert) - 2} столбцов ' + \
                '(не учитывая id)')
        return
    
    # добавление id
    if input_with_id:
        values = values[1:]
        ID = values[0]
        if ID in table_to_insert['id']:
            print('Такой id уже есть.')
            return
    else:
        if not table_to_insert['id']:
            ID = 1
        else:
            ID = max(table_to_insert['id']) + 1
    table_to_insert['id'].append(ID)

    # валидация данных
    for table in metadata:
        if table['table_name'] == table_name:
            columns = table['columns']
    for value, column_type in zip(values, list(columns.values())[1:]):
        match column_type:
            case 'int':
                if not isinstance(value, int):
                    print(f'Значение {value} не соответствует типу колноки int')
                    return
            case 'str':
                if not isinstance(value, str):
                    print(f'Значение {value} не соответствует типу колноки str')
                    return
            case 'bool':
                if not isinstance(value, bool):
                    print(f'Значение {value} не соответствует типу колноки bool')
                    return

    # вставка данных
    columns_to_insert = [col_name for col_name in table_to_insert.keys() 
                         if col_name not in ('table_name', 'id')]
    for value, col_name in zip(values, columns_to_insert):
        table_to_insert[col_name].append(value)
    utils.save_table_data(table_name, table_to_insert)
    print('Данные успешно добавлены.')


def select_ids_by_where_clause(clause, table_data):
    col_name, cond = list(clause.items())[0]
    ids_to_select = []
    col_to_select = table_data[col_name]
    for i in range(len(col_to_select)):
        if col_to_select[i] == cond:
            ids_to_select.append(table_data['id'][i])
    return ids_to_select


def print_prettytable(data):
    row_count = len(next(iter(data.values()), []))
    rows = []
    for i in range(row_count):
        row = {col: values[i] for col, values in data.items()}
        rows.append(row)
        
    table = PrettyTable()
    table.field_names = rows[0].keys()

    for row in rows:
        table.add_row(row.values())

    print(table)


def select(table_name, where_clause=None):
    table_data = utils.load_table_data(table_name)
    if not table_data:
        print('Такой таблицы не существует.')
        return
    
    if len(table_data.get('id', [])) == 0:
        print(f'Таблица {table_name} пуста.')
        return
    
    full_data = {k: v for k, v in table_data.items() if k != "table_name"}

    if where_clause is None:
        print_prettytable(full_data)
        return

    ids_to_select = select_ids_by_where_clause(where_clause, full_data)
    if not ids_to_select:
        print('Записей с таким условмием не найдено.')
        return

    selected = {k: [] for k in full_data.keys()}
    for ID in ids_to_select:
        ind = full_data['id'].index(ID)
        for k in full_data.keys():
            selected[k].append(full_data[k][ind])

    print_prettytable(selected)


def update(table_name, set_clause, where_clause):
    table_data = utils.load_table_data(table_name)
    if not table_data:
            print('Такой таблицы не существует.')
            return 
    
    col_name, value = list(set_clause.items())[0]
    if col_name.lower() == 'id':
        print('Нельзя менять id в ручную.')
        return
    
    ids_to_select = select_ids_by_where_clause(
        where_clause,
        {k: v for k, v in table_data.items() if k != 'table_name'}
    )
    if not ids_to_select:
        print('Записей с таким условмием не найдено.')
        return

    for ID in ids_to_select:
        ind = table_data['id'].index(ID)
        table_data[col_name][ind] = value
    utils.save_table_data(table_name, table_data)

    field = 'Запись' if len(ids_to_select) == 1 else 'Записи'
    deleted = 'обновлена' if len(ids_to_select) == 1 else 'обновлены'
    print(f'{field} с ID = {ids_to_select} успешно {deleted} из таблицы {table_name}.')


def delete(table_name, where_clause):
    table_data = utils.load_table_data(table_name)
    if not table_data:
        print('Такой таблицы не существует.')
        return 

    ids_to_select = select_ids_by_where_clause(
        where_clause,
        {k: v for k, v in table_data.items() if k != 'table_name'}
    )
    if not ids_to_select:
        print('Записей с таким условмием не найдено.')
        return

    indices = sorted(
        [table_data['id'].index(ID) for ID in ids_to_select],
        reverse=True,   
    )

    for ind in indices:
        for col in table_data:
            if col != "table_name":
                del table_data[col][ind]

    utils.save_table_data(table_name, table_data)

    field = 'Запись' if len(indices) == 1 else 'Записи'
    deleted = 'удалена' if len(indices) == 1 else 'удалены'
    print(f'{field} с ID = {ids_to_select} успешно {deleted} из таблицы {table_name}.')


def info(table_name, metadata):
    table_exists = False
    for t in metadata:
        if t['table_name'] == table_name:
            table = t
            table_exists = True
    
    if not table_exists:
        print('Такой таблицы не существует.')
        return

    columns = ', '.join(f'{key}:{value}' for key, value in table['columns'].items())

    table_data = utils.load_table_data(table_name)
    record_count = len(table_data["id"]) if "id" in table_data else 0

    print(f'Таблица: {table_name}')
    print(f'Столбцы: {columns}')
    print(f'Количество записей: {record_count}')








