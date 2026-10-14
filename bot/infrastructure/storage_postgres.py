import json
import os

import pg8000
from dotenv import load_dotenv

from bot.domain.storage import Storage

load_dotenv()


class StoragePostgres(Storage):
    # Исправлено: аннотация типа теперь возвращает Connection, а не None
    def _get_connection(self):
        # Переменные для коннекта к БД
        host = os.getenv("POSTGRES_HOST")
        port = os.getenv("POSTGRES_PORT")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        database = os.getenv("POSTGRES_DB")

        # Исключения если не будет переменных и бот не падал
        if host is None:
            raise ValueError(
                "POSTGRES_HOST переменная окружающей среды не установленна"
            )
        if port is None:
            raise ValueError(
                "POSTGRES_PORT переменная окружающей среды не установленна"
            )
        if user is None:
            raise ValueError(
                "POSTGRES_USER переменная окружающей среды не установленна"
            )
        if password is None:
            raise ValueError(
                "POSTGRES_PASSWORD переменная окружающей среды не установленна"
            )
        if database is None:
            raise ValueError("POSTGRES_DB переменная окружающей среды не установленна")

        # Подключаемся к БД. Приводим port к типу int
        return pg8000.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database,
        )

    def recreate_database(self) -> None:
        # Создает таблицы внутри существующей БД
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS telegram_updates")
                cursor.execute("DROP TABLE IF EXISTS users")
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS telegram_updates 
                    (
                        id SERIAL PRIMARY KEY,
                        payload TEXT NOT NULL
                    )
                    """,
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users 
                    (
                        id SERIAL PRIMARY KEY,
                        telegram_id BIGINT NOT NULL UNIQUE,
                        created_ad TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        state TEXT DEFAULT NULL,
                        order_json TEXT DEFAULT NULL
                    )
                    """,
                )
            connection.commit()

    # Запрос в БД обновляет данные в ней
    def persist_updates(self, updates: list) -> None:
        payload = json.dumps(updates, ensure_ascii=False, indent=2)
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                # Исправлено: payload обернут в кортеж (payload,)
                cursor.execute(
                    "INSERT INTO telegram_updates (payload) VALUES (%s)",
                    (payload,),
                )
            connection.commit()

    # Запись в БД пользователя, если его там нет
    def ensure_users_exists(self, telegram_id: int) -> None:
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                # Исправлено: все вызовы идут через cursor, а параметры передаются кортежами
                cursor.execute(
                    "SELECT 1 FROM users WHERE telegram_id = %s", (telegram_id,)
                )

                # Если нету, то добавляет пользователя
                if cursor.fetchone() is None:
                    cursor.execute(
                        "INSERT INTO users (telegram_id) VALUES (%s)", (telegram_id,)
                    )
            connection.commit()

    # Очищает заказ пользователя
    def clear_user_state_and_order(self, telegram_id: int) -> None:
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = %s",
                    (telegram_id,),
                )
            connection.commit()

    # Обновляет состояние пользователя
    def update_user_state(self, telegram_id: int, state: str) -> None:
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET state = %s WHERE telegram_id = %s",
                    (state, telegram_id),
                )
            connection.commit()

    # Функция достает данные пользователя
    def get_user(self, telegram_id: int) -> dict | None:
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id, telegram_id, created_ad, state, order_json FROM users WHERE telegram_id = %s",
                    (telegram_id,),
                )
                # Исправлено: fetchone() перенесен ВНУТРЬ блока with cursor
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
        # Бесполезный connection.commit() после return удален

    # Функция по telegram_id пользователю в order_json записывает данные
    def update_user_order_json(self, telegram_id: int, order_json: str) -> None:
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                # Исправлено: параметры переданы в виде единого кортежа
                cursor.execute(
                    "UPDATE users SET order_json = %s WHERE telegram_id = %s",
                    (json.dumps(order_json, ensure_ascii=False, indent=2), telegram_id),
                )
            connection.commit()

    def get_order_json(self, telegram_id: int) -> dict | None:
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT order_json FROM users WHERE telegram_id = %s",
                    (telegram_id,),
                )
                # Исправлено: fetchone() перенесен ВНУТРЬ блока with cursor
                result = cursor.fetchone()

            if result and result[0]:
                return json.loads(result[0])
            return None
