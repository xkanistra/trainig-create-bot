# Хендлер принимает подтверждение заказа

import json
import bot.telegram_client
import bot.database_client
from bot.handlers.handler import Handler, HandlerStatus


class OrderConfirm(Handler):
    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_ORDER":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("confirm_")

    def handle(self, update: dict, state: str, order_json: dict) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        chat_id = update["callback_query"]["message"]["chat"]["id"]
        message_id = update["callback_query"]["message"]["message_id"]

        callback_data = update["callback_query"]["data"]

        bot.database_client.update_user_order_json(telegram_id, order_json)
        bot.database_client.update_user_state(telegram_id, "ORDER_CONFIRM")

        try:
            bot.telegram_client.answerCallbackQuery(update["callback_query"]["id"])
        except Exception:
            pass

        bot.telegram_client.makeRequest(
            "editMessageText",
            chat_id=chat_id,
            message_id=message_id,
            text="Ваш заказ подтвержден✅\nОжидайте курьера",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {
                                "text": "Сделать новый заказ",
                                "callback_data": "new_order",
                            },
                        ],
                    ]
                }
            ),
        )
        return HandlerStatus.STOP
