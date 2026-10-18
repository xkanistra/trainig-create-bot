# Хендлер принимает отмену заказа

import json

import httpx

from bot.domain.messenger import Messenger
from bot.domain.order_state import OrderState
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class OrderCancel(Handler):
    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        if "callback_query" not in update:
            return False

        if state != OrderState.WAIT_FOR_ORDER:
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("cancel_")

    async def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        chat_id = update["callback_query"]["message"]["chat"]["id"]
        message_id = update["callback_query"]["message"]["message_id"]

        await storage.update_user_order_json(telegram_id, order_json)
        await storage.update_user_state(telegram_id, OrderState.ORDER_CANCEL)

        try:
            await messenger.answerCallbackQuery(update["callback_query"]["id"])
        # Перехватываем только ошибки сети Telegram API
        except httpx.HTTPStatusError:
            pass

        await messenger.makeRequest(
            "editMessageText",
            chat_id=chat_id,
            message_id=message_id,
            text="❌ Ваш заказ успешно отменен. Будем рады видеть вас снова!\nЧтобы сделать новый заказ, нажмите на кнопку ниже или введите команду /start.",
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
