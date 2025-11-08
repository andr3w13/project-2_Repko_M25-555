# Примитивная БД

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

#### Демонстрация работы
[![asciicast](https://asciinema.org/a/RvlgxVZvK3DPmsCOMLeI2yegl.svg)](https://asciinema.org/a/RvlgxVZvK3DPmsCOMLeI2yegl)
