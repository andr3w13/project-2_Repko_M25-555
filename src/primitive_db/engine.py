import prompt
import shlex
from src.primitive_db import core
from src.primitive_db import utils


def print_help():
    """Prints the help message for the current mode."""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    DATA_JSON_PATH = '/home/andrew/Рабочий стол/МИФИ/Проекты по Python/' \
    'Simple DB/project-2_Repko_M25-555/src/primitive_db/db_meta.json'
    while True:
        data = utils.load_metadata(DATA_JSON_PATH)
        user_input = prompt.string('>>>Введите команду ')
        args = shlex.split(user_input)
        match args[0]:
            case 'create_table':
                columns = {}
                for column in args[2:]:
                    column_name, column_type = column.split(':')
                    columns.update({column_name: column_type})
                core.create_table(data, args[1], columns)
                utils.save_metadata(DATA_JSON_PATH, data)
            case 'drop_table':
                core.drop_table(data, args[1])
                utils.save_metadata(DATA_JSON_PATH, data)
            case 'list_tables':
                if data:
                    for table in data:
                        print(f'- {table['table_name']}')
                else:
                    print('Нет сохраненных таблиц.')
            case 'help':
                print_help()
            case 'exit':
                break
            case _:
                print('Неизвестная команда.')