def create_table(metadata, table_name, columns):
    if all(value in ('int', 'str', 'bool') for _, value in columns.items()):
        if table_name not in metadata['tables']:
            metadata[table_name]['columns'] = {'ID': 'int'}.update(columns)
        else:
            print('Такая таблица уже существует.')
    else:
        print('Недопустимые типы данных. Можно использовать только int, bool, str.')


def drop_table(metadata, table_name):
    if metadata[table_name]:
        del metadata[table_name]
    else:
        print('Такой таблицы не существует.')    