import functools
import time


def handle_db_errors(func):
    """
    Декоратор для обработки ошибок, возникающих при работе с базой данных.
    
    Перехватывает типичные ошибки (FileNotFoundError, KeyError, ValueError,
    IndexError) и выводит понятные сообщения пользователю, после чего
    пробрасывает исключение дальше.
    
    Применяется к функциям, которые читают и модифицируют файлы таблиц.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except FileNotFoundError:
            print('Ошибка: файл данных не найден.')
            raise

        except KeyError as e:
            print(f'Ошибка: отсутствует ключ или столбец: {e}')
            raise

        except ValueError as e:
            print(f'Ошибка валидации: {e}')
            raise

        except IndexError:
            print('Команда введена неправильно. Введите help.')
            raise

    return wrapper


def confirm_action(action_name):
    """
    Декоратор для подтверждения потенциально опасных операций.
    
    Перед вызовом функции спрашивает пользователя, действительно ли он хочет
    выполнить действие (например, удаление таблицы или записей).
    
    Аргументы:
        action_name — строка с описанием действия (используется в сообщении).
    """

    def real_decorator(func):
        def wrapper(*args, **kwargs):
            user_input = input('Вы уверены, что хотите ' + 
                               f'выполнить {action_name}? [y/n]: ')
            if user_input.lower() != 'y':
                print("Операция отменена.")
                return
            return func(*args, **kwargs)
        return wrapper
    return real_decorator


def log_time(func):
    """
    Декоратор для измерения времени выполнения функции.
    
    Выводит время выполнения в формате:
    'Функция <имя> выполнилась за X.XXX секунд.'
    
    Используется для замера скорости операций select и insert.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()
        elapsed = end - start
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")
        return result
    return wrapper


def create_cacher():
    """
    Создает замыкание для кэширования результатов.
    
    Возвращает пару:
        cache_result — функция, принимающая ключ и функцию-вычислитель.
        cache — словарь с текущим состоянием кэша.
    
    При повторных вызовах с одинаковым ключом возвращается сохранённый результат,
    без повторного вычисления.
    
    Используется для оптимизации запросов select.
    """
    
    cache = {}   

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result

    return cache_result, cache
