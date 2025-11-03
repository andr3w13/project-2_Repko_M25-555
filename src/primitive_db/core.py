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


def drop_table(metadata, table_name):
    for i, table in enumerate(metadata):
        if table['table_name'] == table_name:
            del metadata[i]
            print(f'Таблица {table_name} удалена.')
            return
    print('Такой таблицы не существует.')
