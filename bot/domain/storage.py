# Создаем интерфейс для БД
from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    def recreate_database(self) -> None: ...

    @abstractmethod
    def persist_updates(self, updates: list) -> None: ...

    @abstractmethod
    def ensure_users_exists(self, telegram_id: int) -> None: ...

    @abstractmethod
    def clear_user_state_and_order(self, telegram_id: int) -> None: ...

    @abstractmethod
    def update_user_state(self, telegram_id: int, state: str) -> None: ...

    @abstractmethod
    def get_user(self, telegram_id: int) -> dict | None: ...

    @abstractmethod
    def update_user_order_json(self, telegram_id: int, order_json: str) -> None: ...

    @abstractmethod
    def get_order_json(self, telegram_id: int) -> dict: ...
