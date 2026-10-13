# Хендлер записывает информацию в БД

from bot.domain.messenger import Messenger
from bot.domain.order_state import OrderState
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class UpdateDatabaseLogger(Handler):
    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        # Возвращает True при любом типе данных
        return True

    def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        # Записыва все полученные данные в БД и возвращаем True, чтобы
        # перешло к другому хендлеру
        storage.persist_updates([update])
        return HandlerStatus.CONTINUE
