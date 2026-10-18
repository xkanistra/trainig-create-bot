import json
import logging
import os
import time

import asyncpg
from dotenv import load_dotenv

from bot.domain.storage import Storage

load_dotenv()

# Настройка логирования для БД запросов
logger = logging.getLogger(__name__)


class StoragePostgres(Storage):
    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None

    async def _get_pool(self) -> asyncpg.Pool:
        if self._pool is not None:
            return self._pool

        # Создать и вернуть connection pool для PostgreSQL
        host = os.getenv("POSTGRES_HOST")
        # УКАЗЫВАТЬ ПОРТ ПОЛЬЗОВАТЕЛЯ
        port = os.getenv("POSTGRES_HOST_PORT")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        database = os.getenv("POSTGRES_DB")

        # Исключения если не будет переменных и бот не падал
        if host is None:
            raise ValueError("POSTGRES_HOST переменная окружающей среды не установлена")
        if port is None:
            raise ValueError(
                "POSTGRES_HOST_PORT переменная окружающей среды не установлена"
            )
        if user is None:
            raise ValueError("POSTGRES_USER переменная окружающей среды не установлена")
        if password is None:
            raise ValueError(
                "POSTGRES_PASSWORD переменная окружающей среды не установлена"
            )
        if database is None:
            raise ValueError("POSTGRES_DB переменная окружающей среды не установлена")

        self._pool = await asyncpg.create_pool(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database,
        )
        return self._pool

    # Закрываем connection pool
    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def init_database(self) -> None:
        method_name = "init_database"
        start_time = time.time()

        logger.info(f"[DB] -> {method_name} - CHECK/CREATE TABLES")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as connection:
                await connection.execute(
                    """
                        CREATE TABLE IF NOT EXISTS telegram_updates 
                        (
                            id SERIAL PRIMARY KEY,
                            payload TEXT NOT NULL
                        )
                    """,
                )
                await connection.execute(
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

                duration_ms = (time.time() - start_time) * 1000
                logger.info(f"[DB] <- {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] X {method_name} - {duration_ms:.2f}ms - ERROR: {e}")
            raise

    # Используется ТОЛЬКО вручную на ПК для тестов
    async def recreate_database(self) -> None:
        logger.warning("[DB] -> ! ВНИМАНИЕ ! Пересоздание базы данных (DROP TABLES)")
        pool = await self._get_pool()
        async with pool.acquire() as connection:
            await connection.execute("DROP TABLE IF EXISTS telegram_updates")
            await connection.execute("DROP TABLE IF EXISTS users")
        await self.init_database()

    # Запрос в БД обновляет данные в ней
    async def persist_updates(self, updates: list) -> None:
        method_name = "persist_updates"
        sql_query = "INSERT INTO telegram_updates (payload) VALUES ($1)"
        start_time = time.time()

        logger.info(f"[DB] -> {method_name} - {sql_query}")

        payload = json.dumps(updates, ensure_ascii=False, indent=2)
        try:
            pool = await self._get_pool()
            async with pool.acquire() as connection:
                # Фикс: Передаем payload напрямую, БЕЗ кортежа (payload,)
                await connection.execute(
                    "INSERT INTO telegram_updates (payload) VALUES ($1)",
                    payload,
                )
                duration_ms = (time.time() - start_time) * 1000
                logger.info(f"[DB] <- {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] X {method_name} - {duration_ms:.2f}ms - ERROR: {e}")
            raise

    async def ensure_users_exists(self, telegram_id: int) -> None:
        method_name = "ensure_users_exists"
        start_time = time.time()

        logger.info(f"[DB] -> {method_name} SELECT/INSERT users")
        try:
            pool = await self._get_pool()
            async with pool.acquire() as connection:
                result = await connection.fetchrow(
                    "SELECT 1 FROM users WHERE telegram_id = $1",
                    telegram_id,
                )

                # Если нету, то добавляет пользователя
                if result is None:
                    # Фикс: Передаем telegram_id напрямую, БЕЗ кортежа
                    await connection.execute(
                        "INSERT INTO users (telegram_id) VALUES ($1)",
                        telegram_id,
                    )
                duration_ms = (time.time() - start_time) * 1000
                logger.info(f"[DB] <- {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] X {method_name} - {duration_ms:.2f}ms - ERROR: {e}")
            raise

    # Очищает заказ пользователя
    async def clear_user_state_and_order(self, telegram_id: int) -> None:
        method_name = "clear_user_state_and_order"
        sql_query = (
            "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = $1"
        )
        start_time = time.time()

        logger.info(f"[DB] -> {method_name} - {sql_query}")
        try:
            pool = await self._get_pool()
            async with pool.acquire() as connection:
                # Фикс: Передаем telegram_id напрямую, БЕЗ кортежа
                await connection.execute(
                    "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = $1",
                    telegram_id,
                )
                duration_ms = (time.time() - start_time) * 1000
                logger.info(f"[DB] <- {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] X {method_name} - {duration_ms:.2f}ms - ERROR: {e}")
            raise

    # Обновляет состояние пользователя
    async def update_user_state(self, telegram_id: int, state: str) -> None:
        method_name = "update_user_state"
        sql_query = "UPDATE users SET state = $1 WHERE telegram_id = $2"
        start_time = time.time()

        logger.info(f"[DB] -> {method_name} - {sql_query}")
        try:
            pool = await self._get_pool()
            async with pool.acquire() as connection:
                # Фикс: Передаем параметры напрямую и убираем кортеж с telegram_id
                await connection.execute(
                    "UPDATE users SET state = $1 WHERE telegram_id = $2",
                    state,
                    telegram_id,
                )
                duration_ms = (time.time() - start_time) * 1000
                logger.info(f"[DB] <- {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] X {method_name} - {duration_ms:.2f}ms - ERROR: {e}")
            raise

    # Функция достает данные пользователя
    async def get_user(self, telegram_id: int) -> dict | None:
        method_name = "get_user"
        sql_query = "SELECT id, telegram_id, created_ad, state, order_json FROM users WHERE telegram_id = $1"
        start_time = time.time()

        logger.info(f"[DB] -> {method_name} - {sql_query}")
        try:
            pool = await self._get_pool()
            async with pool.acquire() as connection:
                result = await connection.fetchrow(
                    "SELECT id, telegram_id, created_ad, state, order_json FROM users WHERE telegram_id = $1",
                    telegram_id,
                )
                if result:
                    user_data = {
                        "id": result["id"],
                        "telegram_id": result["telegram_id"],
                        "created_ad": result["created_ad"],
                        "state": result["state"],
                        # Если в базе лежит строка, возвращаем как есть; диспетчер сам распарсит
                        "order_json": result["order_json"],
                    }
                    duration_ms = (time.time() - start_time) * 1000
                    logger.info(f"[DB] <- {method_name} - {duration_ms:.2f}ms")
                    return user_data

                # Если пользователя нет в базе
                duration_ms = (time.time() - start_time) * 1000
                logger.info(
                    f"[DB] <- {method_name} (User not found) - {duration_ms:.2f}ms"
                )
                return None
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] X {method_name} - {duration_ms:.2f}ms - ERROR: {e}")
            raise

    # Функция по telegram_id пользователю в order_json записывает данные
    # Фикс: Принимаем dict, так как хендлеры передают объект словаря
    async def update_user_order_json(self, telegram_id: int, order_json: dict) -> None:
        method_name = "update_user_order_json"
        sql_query = "UPDATE users SET order_json = $1 WHERE telegram_id = $2"
        start_time = time.time()

        logger.info(f"[DB] -> {method_name} - {sql_query}")
        try:
            pool = await self._get_pool()
            async with pool.acquire() as connection:
                # Фикс: Сериализуем переданный словарь в чистую JSON-строку
                json_string = json.dumps(order_json, ensure_ascii=False)

                # Фикс: Заменили %s на $1, $2 для asyncpg
                await connection.execute(
                    "UPDATE users SET order_json = $1 WHERE telegram_id = $2",
                    json_string,
                    telegram_id,
                )

                duration_ms = (time.time() - start_time) * 1000
                logger.info(f"[DB] <- {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] X {method_name} - {duration_ms:.2f}ms - ERROR: {e}")
            raise

    async def get_order_json(self, telegram_id: int) -> dict:
        method_name = "get_order_json"
        start_time = time.time()

        logger.info(f"[DB] -> {method_name} SELECT users")
        try:
            pool = await self._get_pool()
            async with pool.acquire() as connection:
                result = await connection.fetchrow(
                    "SELECT order_json FROM users WHERE telegram_id = $1",
                    telegram_id,
                )

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")

            # Фикс: Должен возвращать dict по контракту интерфейса. Если пусто, возвращаем {}
            if result and result["order_json"]:
                return json.loads(result["order_json"])
            return {}

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise
