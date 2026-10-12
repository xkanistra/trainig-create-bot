# Хендлер обрабатывает нажатие выбора размера пиццы

import json

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class PizzaSize(Handler):
    def can_handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        # Если нету callback в update, вернуть False
        if "callback_query" not in update:
            return False

        # Если состояние из которого пришел callback, состояние достает dispatch из БД
        # не равен выбору названия пиццы вернуть False
        if state != "WAIT_FOR_PIZZA_SIZE":
            return False

        # Достаем данные о пиццах, в дате будет название из callback_data
        # в message_start.py
        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("size_")

    def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        # Достаем telegram_id и callback_data из update. Они точно есть т.к can_handle это проверяет
        telegram_id = update["callback_query"]["from"]["id"]
        chat_id = update["callback_query"]["message"]["chat"]["id"]
        message_id = update["callback_query"]["message"]["message_id"]

        callback_data = update["callback_query"]["data"]

        size_mapping = {
            "size_small": "Маленькая (25см)",
            "size_medium": "Средняя (30см)",
            "size_large": "Большая (35см)",
            "size_xl": "Очень большая (40см)",
        }

        pizza_size = size_mapping.get(callback_data)
        order_json["pizza_size"] = pizza_size

        storage.update_user_order_json(telegram_id, order_json)
        storage.update_user_state(telegram_id, "WAIT_FOR_DRINKS")

        messenger.answerCallbackQuery(update["callback_query"]["id"])

        messenger.makeRequest(
            "editMessageText",
            chat_id=chat_id,
            message_id=message_id,
            text="Пожалуйста выберите напиток",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {"text": "Coca-Cola", "callback_data": "drink_coca_cola"},
                            {"text": "Fanta", "callback_data": "drink_fanta"},
                        ],
                        [
                            {"text": "Pepsi", "callback_data": "drink_pepsi"},
                            {"text": "7-Up", "callback_data": "drink_7_up"},
                        ],
                        [
                            {"text": "Вода", "callback_data": "drink_water"},
                            {"text": "Без напитка", "callback_data": "drink_none"},
                        ],
                        [
                            {"text": "⬅️ Назад", "callback_data": "back_to_pizza_size"},
                        ],
                    ]
                }
            ),
        )
        return HandlerStatus.STOP
