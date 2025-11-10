import os

from prettytable import PrettyTable

from src.primitive_db import constants, decorators, utils


@decorators.handle_db_errors
def create_table(metadata, table_name, columns):
    """
    Создаёт новую таблицу в метаданных и создаёт соответствующий JSON-файл.

    Аргументы:
        metadata (list): список словарей с описанием всех таблиц.
        table_name (str): имя создаваемой таблицы.
        columns (dict): словарь вида {column_name: type}, 
        где type in {'int', 'str', 'bool'}.

    Поведение:
        • проверяет корректность типов столбцов;
        • не допускает создание таблицы с существующим именем;
        • автоматически добавляет столбец id, если он не указан;
        • создаёт пустой JSON-файл для таблицы;
        • очищает кэш SELECT.
    """

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

    constants.SELECT_CACHE_STORE.clear()


@decorators.handle_db_errors
@decorators.confirm_action('удаление таблицы')
def drop_table(metadata, table_name):
    """
    Удаляет таблицу из метаданных и физически удаляет её JSON-файл.

    Аргументы:
        metadata (list): список таблиц.
        table_name (str): имя удаляемой таблицы.

    Поведение:
        • проверяет, существует ли таблица;
        • удаляет её запись из метаданных;
        • удаляет файл таблицы, если он существует;
        • очищает кэш SELECT.
    """

    for i, table in enumerate(metadata):
        if table['table_name'] == table_name:
            del metadata[i]
            table_path = utils.get_table_path(table_name)
            if os.path.exists(table_path):
                os.remove(table_path)
            print(f'Таблица {table_name} удалена.')
            return
    print('Такой таблицы не существует.')
    constants.SELECT_CACHE_STORE.clear()


def clean_values(values):
    """
    Подготавливает значения INSERT: убирает скобки/запятые и приводит типы.

    Аргументы:
        values (list[str]): сырые строковые значения из команды INSERT.

    Возвращает:
        tuple: очищенные и сконвертированные значения (int, float, bool или str).
    """

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


@decorators.handle_db_errors
@decorators.log_time
def insert(metadata, table_name, values):
    """
    Добавляет строку в таблицу.

    Аргументы:
        metadata (list): список таблиц.
        table_name (str): имя таблицы.
        values (list[str]): значения, переданные пользователем.

    Поведение:
        • определяет ID автоматически или принимает от пользователя;
        • проверяет соответствие типов значений столбцам;
        • добавляет новые данные в JSON-файл таблицы;
        • очищает кэш SELECT.
    """

    values = clean_values(values)

    # проверка на существование таблицы
    if metadata and any(table['table_name'] == table_name for table in metadata):
        table_to_insert = utils.load_table_data(table_name)
        if not table_to_insert:
            print('Произошла ошибка, попробуйте снова')
            return
    else:
        print('Такой таблицы не существует.')
        return
        
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
    
    constants.SELECT_CACHE_STORE.clear()


def select_ids_by_where_clause(clause, table_data):
    """
    Возвращает список ID записей, удовлетворяющих условию WHERE.

    Аргументы:
        clause (dict): условие вида {column: value}.
        table_data (dict): данные таблицы без поля table_name.

    Возвращает:
        list[int]: ID подходящих записей.
    """

    col_name, cond = list(clause.items())[0]
    ids_to_select = []
    col_to_select = table_data[col_name]
    for i in range(len(col_to_select)):
        if col_to_select[i] == cond:
            ids_to_select.append(table_data['id'][i])
    return ids_to_select


def print_prettytable(data):
    """
    Печатает данные таблицы в формате PrettyTable.

    Аргументы:
        data (dict): данные таблицы без поля table_name,
                     все значения — списки одинаковой длины.
    """

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


@decorators.handle_db_errors
@decorators.log_time
def select(table_name, where_clause=None):
    """
    Выбирает данные из таблицы с учётом кэширования и условия WHERE.

    Аргументы:
        table_name (str): имя таблицы.
        where_clause (dict | None): условие выбора, например {"age": 18}.

    Поведение:
        • загружает данные таблицы;
        • если where_clause нет — выводит все строки;
        • если есть — выводит только отфильтрованные строки;
        • использует кэширование результатов;
        • выводит таблицу через PrettyTable.
    """

    cache_key = (table_name, tuple(where_clause.items()) if where_clause else None)

    def compute():
        table_data = utils.load_table_data(table_name)
        if not table_data:
            return 'NO_TABLE'

        if len(table_data.get('id', [])) == 0:
            return 'EMPTY'

        full_data = {k: v for k, v in table_data.items() if k != 'table_name'}

        if where_clause is None:
            return full_data

        ids = select_ids_by_where_clause(where_clause, full_data)
        if not ids:
            return 'NO_RESULTS'

        selected = {k: [] for k in full_data}
        for ID in ids:
            ind = full_data['id'].index(ID)
            for col in full_data:
                selected[col].append(full_data[col][ind])
        return selected

    result = constants.SELECT_CACHE(cache_key, compute)

    if result == 'NO_TABLE':
        print('Такой таблицы не существует.')
        return

    if result == 'EMPTY':
        print(f'Таблица {table_name} пуста.')
        return

    if result == 'NO_RESULTS':
        print('Записей с таким условием не найдено.')
        return

    print_prettytable(result)


@decorators.handle_db_errors
@decorators.log_time
def update(table_name, set_clause, where_clause):
    """
    Обновляет значения в строках таблицы, удовлетворяющих WHERE.

    Аргументы:
        table_name (str): имя таблицы.
        set_clause (dict): новое значение, например {"name": "Ivan"}.
        where_clause (dict): условие выбора строк.

    Поведение:
        • проверяет существование таблицы;
        • запрещает изменять ID;
        • обновляет все подходящие строки;
        • сохраняет изменения в файл;
        • очищает кэш SELECT.
    """

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

    constants.SELECT_CACHE_STORE.clear()


@decorators.handle_db_errors
@decorators.confirm_action('удаление записи')
def delete(table_name, where_clause):
    """
    Удаляет строки таблицы, удовлетворяющие условию WHERE.

    Аргументы:
        table_name (str): имя таблицы.
        where_clause (dict): условие удаления.

    Поведение:
        • находит строки, соответствующие условию;
        • удаляет строки по индексам;
        • сохраняет обновлённые данные;
        • очищает кэш SELECT.
    """

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

    constants.SELECT_CACHE_STORE.clear()


@decorators.handle_db_errors
def info(table_name, metadata):
    """
    Выводит информацию о таблице: название, столбцы, количество записей.

    Аргументы:
        table_name (str): имя таблицы.
        metadata (list): список таблиц.

    Поведение:
        • проверяет существование таблицы;
        • выводит список столбцов с типами;
        • считает число записей по длине списка id.
    """

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
    record_count = len(table_data['id']) if 'id' in table_data else 0

    print(f'Таблица: {table_name}')
    print(f'Столбцы: {columns}')
    print(f'Количество записей: {record_count}')
