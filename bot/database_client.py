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
        connection.execute("DROP TABLE IF EXISTS users")
        connection.execute(
            """
        CREATE TABLE IF NOT EXISTS telegram_updates 
        (
            id INTEGER PRIMARY KEY,
            payload TEXT NOT NULL
        )
        """,
        )
        connection.execute(
            """
        CREATE TABLE IF NOT EXISTS users 
        (
            id INTEGER PRIMARY KEY,
            telegram_id INTEGER NOT NULL UNIQUE,
            created_ad TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            state TEXT DEFAULT NULL,
            order_json TEXT DEFAULT NULL
        )
        """,
        )


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


# Запись в БД пользователя, если есть и если нету
def ensure_users_exists(telegram_id: int) -> None:
    with sqlite3.connect(getenv("SQLITE_DATABASE_PATH")) as connection:
        # Проверяет есть ли пользователь в БД с таким ID
        cursor = connection.execute(
            "SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,)
        )

        # Если нету, то добавляет пользователя
        if cursor.fetchone() is None:
            connection.execute(
                "INSERT INTO users (telegram_id) VALUES (?)", (telegram_id,)
            )


# Очищает заказ пользователя
def clear_user_state_and_order(telegram_id: int) -> None:
    with sqlite3.connect(getenv("SQLITE_DATABASE_PATH")) as connection:
        with connection:
            connection.execute(
                "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = ?",
                (telegram_id,),
            )


# Обновляет состояние пользователя
def update_user_state(telegram_id: int, state: str) -> None:
    with sqlite3.connect(getenv("SQLITE_DATABASE_PATH")) as connection:
        with connection:
            connection.execute(
                "UPDATE users SET state = ? WHERE telegram_id = ?",
                (state, telegram_id),
            )


# Функция достает пользовательский id
def get_user(telegram_id: int) -> dict | None:
    with sqlite3.connect(getenv("SQLITE_DATABASE_PATH")) as connection:
        with connection:
            # Запрос в БД по telegram_id
            cursor = connection.execute(
                "SELECT id, telegram_id, created_ad, state, order_json FROM users WHERE telegram_id = (?)",
                (telegram_id,),
            )
            # Достаем только одну запись, т.к telegram_id уникален
            result = cursor.fetchone()
            if result:
                return {
                    "id": result[0],
                    "telegram_id": result[1],
                    "created_ad": result[2],
                    "state": result[3],
                    "order_json": result[4],
                }
            return None


# Функция по telegram_id пользователю в order_json записывает данные
def update_user_order_json(telegram_id: int, order_json: str) -> None:
    with sqlite3.connect(getenv("SQLITE_DATABASE_PATH")) as connection:
        with connection:
            connection.execute(
                "UPDATE users SET order_json = ? WHERE telegram_id = ?",
                (json.dumps(order_json, ensure_ascii=False, indent=2), telegram_id)
            )
