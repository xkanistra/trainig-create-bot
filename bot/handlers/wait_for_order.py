# Хендлер подтверждения заказа

import json
import bot.telegram_client
import bot.database_client
from bot.handlers.handler import Handler, HandlerStatus


class WaitForOrder(Handler):
    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_DRINKS":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("drink_")

    def handle(self, update: dict, state: str, order_json: dict) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        chat_id = update["callback_query"]["message"]["chat"]["id"]
        message_id = update["callback_query"]["message"]["message_id"]

        callback_data = update["callback_query"]["data"]

        drink_mapping = {
            "drink_coca_cola": "Coca-Cola",
            "drink_fanta": "Fanta",
            "drink_pepsi": "Pepsi",
            "drink_7_up": "7-Up",
            "drink_water": "Вода",
        }

        drink_name = drink_mapping.get(callback_data)
        order_json["drink_name"] = drink_name

        bot.database_client.update_user_order_json(telegram_id, order_json)
        bot.database_client.update_user_state(telegram_id, "WAIT_FOR_ORDER")

        bot.telegram_client.answerCallbackQuery(update["callback_query"]["id"])

        bot.telegram_client.makeRequest(
            "editMessageText",
            chat_id=chat_id,
            message_id=message_id,
            text=f"Подтвердите ваш заказ:\n",
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
