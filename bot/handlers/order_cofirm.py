# Хендлер принимает подтверждение заказа

import json

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class OrderConfirm(Handler):
    def can_handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_ORDER":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("confirm_")

    def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        chat_id = update["callback_query"]["message"]["chat"]["id"]
        message_id = update["callback_query"]["message"]["message_id"]

        update["callback_query"]["data"]

        storage.update_user_order_json(telegram_id, order_json)
        storage.update_user_state(telegram_id, "ORDER_CONFIRM")

        try:
            messenger.answerCallbackQuery(update["callback_query"]["id"])
        except Exception:
            pass

        messenger.makeRequest(
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
