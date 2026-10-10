# Хендлер обрабатывает нажатие выбора пиццы

import json
import bot.telegram_client
import bot.database_client
from bot.handlers.handler import Handler, HandlerStatus


class PizzaSelection(Handler):
    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        print(f"DEBUG: Текущее состояние из БД = '{state}'")
        # Если нету callback в update, вернуть False
        if "callback_query" not in update:
            return False

        # Если состояние из которого пришел callback, состояние достает dispatch из БД
        # не равен выбору названия пиццы вернуть False
        if state != "WAIT_FOR_PIZZA_NAME":
            return False

        # Достаем данные о пиццах, в дате будет название из callback_data
        # в message_start.py
        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("pizza_")

    def handle(self, update: dict, state: str, order_json: dict) -> HandlerStatus:
        # Достаем telegram_id и callback_data из update. Они точно есть т.к can_handle это проверяет
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        # Форматируем название пиццы из callback, убираем pizza_ , _ и приводим к верх.регистру
        pizza_name = callback_data.replace("pizza_", "").replace("_", " ").title()
        # Блок обновляет состояние и добавляет название заказываемой пиццы
        bot.database_client.update_user_order_json(telegram_id, {"pizza_name": pizza_name})
        bot.database_client.update_user_state(telegram_id, "WAIT_FOR_PIZZA_SIZE")

        # Данная строка убирает визуальное колесо загрузки
        bot.telegram_client.answerCallbackQuery(update["callback_query"]["id"])
        # Функция удаляет предыдущее сообщение, чтобы не было историй СМС от бота
        bot.telegram_client.deleteMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )
        bot.telegram_client.sendMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text="Пожалуйста выберите размер пиццы",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {"text": "Маленькая (25см)", "callback_data": "size_small"},
                            {"text": "Средняя (30см)", "callback_data": "size_medium"},
                        ],
                        [
                            {"text": "Большая (35см)", "callback_data": "size_large"},
                            {
                                "text": "Очень большая (40см)",
                                "callback_data": "size_xl",
                            },
                        ],
                    ]
                }
            ),
        )
        return HandlerStatus.STOP
