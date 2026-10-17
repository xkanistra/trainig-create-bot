import json
import logging
from os import getenv
import time

import asyncpg
from dotenv import load_dotenv

from bot.domain.storage import Storage

load_dotenv()

# Настройка логирования для БД запросов
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s.%(msecs)03d] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class StoragePostgres(Storage):
    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None

    async def _get_pool(self) -> asyncpg.Pool:
        if self._pool is not None:
            return self._pool

        # Создать и вернуть connection pool для PostgreSQL
        host = "127.0.0.1"
        port = 5433
        user = "postgres"
        password = "postgres"
        database = "pizza_bot_test"

        # Исключения если не будет переменных и бот не падал
        if host is None:
            raise ValueError(
                "POSTGRES_HOST переменная окружающей среды не установленна"
            )
        if port is None:
            raise ValueError(
                "POSTGRES_HOST_PORT переменная окружающей среды не установленна"
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
            await self._pool.closed()
            self._pool = None

    async def recreate_database(self) -> None:
        method_name = "recreate_database"
        start_time = time.time()

        logger.info(f"[DB] -> {method_name} - DROP/CREATE TABLES")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as connection:
                await connection.execute("DROP TABLE IF EXISTS telegram_updates")
                await connection.execute("DROP TABLE IF EXISTS users")
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
                result = await connection.fetchowr(
                    "SELECT 1 FROM users WHERE telegram_id = $1",
                    telegram_id,
                )

                # Если нету, то добавляет пользователя
                if result is None:
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
                        "order_json": result["order_json"],
                    }
                    duration_ms = (time.time() - start_time) * 1000
                    logger.info(f"[DB] <- {method_name} - {duration_ms:.2f}ms")
                    return user_data
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] X {method_name} - {duration_ms:.2f}ms - ERROR: {e}")
            raise

    # Функция по telegram_id пользователю в order_json записывает данные
    async def update_user_order_json(self, telegram_id: int, order_json: str) -> None:
        method_name = "update_user_order_json"
        sql_query = "UPDATE users SET order_json = $1 WHERE telegram_id = $2"
        start_time = time.time()

        logger.info(f"[DB] -> {method_name} - {sql_query}")
        try:
            pool = await self._get_pool()
            async with pool.acquire() as connection:
                connection.execute(
                    "UPDATE users SET order_json = %s WHERE telegram_id = %s",
                    json.dumps(order_json, ensure_ascii=False, indent=2),
                    telegram_id,
                )

                duration_ms = (time.time() - start_time) * 1000
                logger.info(f"[DB] <- {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] X {method_name} - {duration_ms:.2f}ms - ERROR: {e}")
            raise

    async def get_order_json(self, telegram_id: int) -> dict | None:
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
            if result and result[0]:
                return json.loads(result[0])

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise
