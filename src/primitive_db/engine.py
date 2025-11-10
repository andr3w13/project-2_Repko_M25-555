import shlex

import prompt

from src.primitive_db import core, utils


def print_help():
    """
    Выводит справочную информацию о доступных командах приложения.

    Показывает описание основных операций:
    создание, просмотр и удаление таблиц, а также общих команд вроде help и exit.
    """
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def parse(col_name, cond):
    """
    Преобразует строковое значение условия в корректный тип данных.

    Определяет, является ли значение булевым, числом или строкой,
    затем возвращает словарь вида: {<имя_столбца>: <значение>}.

    Используется для обработки команд WHERE и SET.
    """

    cond = cond.strip()

    if cond.lower() == "true":
        return {col_name: True}
    if cond.lower() == "false":
        return {col_name: False}

    if cond.lstrip("-").isdigit():
        return {col_name: int(cond)}
    
    return {col_name: cond}


def run():
    """
    Запускает основной цикл обработки пользовательских команд.

    Принимает текстовые команды, разбирает их,
    вызывает соответствующие функции ядра (core.py):
    create_table, insert, select, update, delete и др.

    Работает до тех пор, пока пользователь не введёт команду exit.
    """
    
    while True:
        data = utils.load_metadata()
        user_input = prompt.string('>>>Введите команду: ')
        args = shlex.split(user_input)
        match args[0]:
            case 'create_table':
                if len(args) < 3:
                    print('Недостаточно аргументов.')
                    continue

                table_name = args[1]
                columns = {}

                for token in args[2:]:
                    try:
                        col, type_ = token.split(':')
                    except ValueError:
                        print(f'Ошибка в аргументе {token}.')
                        break
                    columns[col] = type_

                core.create_table(data, table_name, columns)
                utils.save_metadata(data)

            case 'drop_table':
                    core.drop_table(data, args[1])
                    utils.save_metadata(data)

            case 'list_tables':
                if data:
                    for table in data:
                        print(f"- {table['table_name']}")
                else:
                    print('Нет сохраненных таблиц.')

            case 'insert':
                table_name = args[2]            
                values_idx = args.index('values')
                raw_values = args[values_idx+1:]
                core.insert(data, table_name, raw_values)
                utils.save_metadata(data)

            case 'select':
                if 'where' in args:
                    where_index = args.index('where')
                    where_clause = parse(args[where_index + 1], args[where_index + 3])
                else:
                    where_clause = None
                core.select(args[2], where_clause)

            case 'update':
                if 'set' not in args or 'where' not in args:
                    print('Команда update должна содержать set и where.')
                    break
                table_name = args[1]
                set_idx = args.index('set')
                set_col = args[set_idx + 1]              
                set_value = args[set_idx + 3]            
                set_clause = parse(set_col, set_value)
                where_idx = args.index('where')
                where_col = args[where_idx + 1]
                where_value = args[where_idx + 3]
                where_clause = parse(where_col, where_value)
                core.update(table_name, set_clause, where_clause)

            case 'delete':
                table_name = args[2]                
                where_idx = args.index('where')
                col = args[where_idx + 1]
                cond = args[where_idx + 3]
                where_clause = parse(col, cond)
                core.delete(table_name, where_clause)

            case 'info':
                core.info(args[1], data)

            case 'help':
                print_help()

            case 'exit':
                break

            case _:
                print('Неизвестная команда.')
