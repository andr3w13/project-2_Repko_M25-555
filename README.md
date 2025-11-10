# Примитивная БД

## Инструкция по установке и запуску
### Установка
Установку можно выполнить двумя сопособами:
1. через Poetry - poetry install
2. через Makefile - make install

### Запуск приложения
Также есть два способа:
1. через Poetry - poetry run database
2. через Makefile - make run

## Демонстрация работы БД
[![asciicast](https://asciinema.org/a/ZYGIC1JMznsM5aNTuJljkxzcK.svg)](https://asciinema.org/a/ZYGIC1JMznsM5aNTuJljkxzcK)

## Управление таблицами
1. create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу.
2. list_tables - показать список всех таблиц.
3. drop_table <имя_таблицы> - удалить таблицу.
4. info <имя_таблицы> - вывести информацию о таблице.
5. help - справочная информация.
6. exit - выход из программы.

#### Примеры использования
1. create_table users name:str age:int is_active:bool
2. list_tables
3. drop_table users

#### Демонстрация работы
[![asciicast](https://asciinema.org/a/5fdNm9sss2s7pRevJGtoJuoEp.svg)](https://asciinema.org/a/5fdNm9sss2s7pRevJGtoJuoEp)

## CRUD-операции
1. insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись.
2. select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию.
3. select from <имя_таблицы> - прочитать все записи.
4. update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись.
5. delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.

#### Примеры использования
1. insert into users values ("Sergei", 28, true)
2. update users set age = 29 where name = "Sergei"
3. delete from users where ID = 1
4. select from users where age = 28

#### Демонстрация работы
[![asciicast](https://asciinema.org/a/RvlgxVZvK3DPmsCOMLeI2yegl.svg)](https://asciinema.org/a/RvlgxVZvK3DPmsCOMLeI2yegl)

## Обработка ошибок
В проект добавлена централизованная система обработки ошибок на основе декоратора @handle_db_errors.
Этот декоратор:
1. перехватывает распространённые ошибки (FileNotFoundError, KeyError, ValueError, IndexError);
2. выводит понятные человеку сообщения;
3. предотвращает аварийное завершение программы;
4. упрощает отладку и повышает стабильность всей базы данных.

## Подтверждение опасных действий
Для операций, приводящих к удалению данных, реализован декоратор @confirm_action.
Он:
1. спрашивает подтверждение перед выполнением операций drop_table и delete;
2. предотвращает случайное удаление таблиц или записей;
3. делает работу с базой данных более безопасной.

#### Демонстрация работы
[![asciicast](https://asciinema.org/a/fkhjGxmr3pWuBU2yi8EqvNPFg.svg)](https://asciinema.org/a/fkhjGxmr3pWuBU2yi8EqvNPFg)