import sqlite3
import json
from os import getenv
from dotenv import load_dotenv

load_dotenv()


# !!!ВАЖНО!!! метод пересоздает БД
# если БД уже была, то можно потерять данные
def recreate_database() -> None:
    # Создает БД, если есть то подключается к ней
    connection = sqlite3.connect(getenv("SQLITE_DATABASE_PATH"))
    # Запрос для создания БД
    with connection:
        # SQL запросы
        connection.execute("DROP TABLE IF EXISTS telegram_updates")
        connection.execute("""
        CREATE TABLE IF NOT EXISTS telegram_updates 
        (
            id INTEGER PRIMARY KEY,
            payload TEXT NOT NULL
        )
        """)
    # Обязательно нужно закрыть
    connection.close()


# Запрос в БД обновляет данные в ней
def persist_updates(updates: list) -> None:
    connection = sqlite3.connect(getenv("SQLITE_DATABASE_PATH"))
    data = []
    for update in updates:
        ## ensure_ascii - по умолчанию True, False позволяет передавать русские символы и т.п
        ## indent - отступы
        ## так же можно указывать как будет отображать данные БД
        data.append((json.dumps(update, ensure_ascii=False),))
    with connection:
        connection.executemany(
            "INSERT INTO telegram_updates (payload) VALUES (?)",
            data,
        )
    connection.close()
