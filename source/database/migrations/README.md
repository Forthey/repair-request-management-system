Создание ревизии (миграция) --> в папке source это команда
```
alembic -c ../alembic.ini revision --autogenerate -m "Имя миграции"
```
Накатить все миграции на бд или какую-то конкретную
```
alembic upgrade head
alembic upgrabe <key>
```
Аналогично, если нужно откатить
```
alembic downgrade base
alembic downgrade <key>
```
Также стоит помнить, что alembic не запоминает enums, так что в downgrade с ним в пару придется ручками  писать
```
op.execute("DROP TYPE ...")
```