# Написание диспетчера

import json
import bot.database_client
from bot.handlers.handler import Handler, HandlerStatus
from bot.tools.json_inspector import inspect


class Dispatcher:
    def __init__(self):
        # Создаем массив хендлеров
        self.__handlers: list[Handler] = []

    # Метод добавляет хендлеры в массив
    def add_handler(self, *handlers: list[Handler]) -> None:
        for handler in handlers:
            self.__handlers.append(handler)

    # Приватный метод обрабатывает update из message и из callback
    def _get_telegram_id_from_update(self, update: dict) -> int | None:
        # update из /start
        if "message" in update:
            return update["message"]["from"]["id"]
        # update от нажатий на кнопки
        elif "callback_query" in update:
            return update["callback_query"]["from"]["id"]
        return None

    # Метод обрабатывает сигнал из хендлера
    def dispatch(self, update: dict) -> None:
        # Получаем ТГ ID
        telegram_id = self._get_telegram_id_from_update(update)
        # Получаем пользователя из БД
        user = bot.database_client.get_user(telegram_id) if telegram_id else None

        # От пользователя получаем состояние
        user_state = user.get("state") if user else None

        # Из колонки order_json получаем order_json
        order_json = user["order_json"] if user else "{}"
        if order_json is None:
            order_json = "{}"
        order_json = json.loads(order_json)

        inspect(update)
        # Перебирает массив
        for handler in self.__handlers:
            # Если хендлер говорит что он все сделал,
            # останавливаем перебор хендлеров
            if handler.can_handle(update, user_state, order_json):
                status = handler.handle(update, user_state, order_json)
                if status == HandlerStatus.STOP:
                    break
