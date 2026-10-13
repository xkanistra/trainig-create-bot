# Хендлер отправляет сообщ при входе пользователя

import json
import urllib.error

from bot.domain.messenger import Messenger
from bot.domain.order_state import OrderState
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class MessageStart(Handler):
    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        # Проверяем условия при отправке смс, что отбросит любой шанс сломать бота смс
        if (
            "message" in update
            and "text" in update["message"]
            and update["message"]["text"] == "/start"
        ):
            return True

        return bool(
            "callback_query" in update
            and update["callback_query"]["data"].startswith("new_")
        )

    def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        # Фильтруем приходящее сообщение, либо это /start либо callback и исходя из этого берем данные
        if "callback_query" not in update:
            telegram_id = update["message"]["from"]["id"]
            chat_id = update["message"]["chat"]["id"]
        else:
            telegram_id = update["callback_query"]["from"]["id"]
            chat_id = update["callback_query"]["message"]["chat"]["id"]
            message_id = update["callback_query"]["message"]["message_id"]
            update["callback_query"]["data"]

        message_command = (
            "message" in update
            and "text" in update["message"]
            and update["message"]["text"] == "/start"
        )

        pizza_keyboard = json.dumps(
            {
                "inline_keyboard": [
                    [
                        {"text": "Маргарита", "callback_data": "pizza_margherita"},
                        {"text": "Пепперони", "callback_data": "pizza_pepperoni"},
                    ],
                    [
                        {
                            "text": "Четыре сыра",
                            "callback_data": "pizza_quatro_stagioni",
                        },
                        {"text": "Капричоза", "callback_data": "pizza_capricciosa"},
                    ],
                    [
                        {"text": "Дьявола", "callback_data": "pizza_diavola"},
                        {"text": "Прошутто", "callback_data": "pizza_prosciutto"},
                    ],
                ],
            }
        )
        # Очищает заказ клиента
        storage.clear_user_state_and_order(telegram_id)
        storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_NAME)

        if message_command:
            messenger.sendMessage(
                chat_id=chat_id,
                text="Добро пожаловать в Пиццерию!",
                reply_markup=json.dumps({"remove_keyboard": True}),
            )

            messenger.sendMessage(
                chat_id=chat_id,
                text="Пожалуйста выберите пиццу",
                reply_markup=pizza_keyboard,
            )
        else:
            try:
                messenger.answerCallbackQuery(update["callback_query"]["id"])
            # Перехватываем только ошибки сети Telegram API
            except urllib.error.HTTPError:
                pass
            messenger.makeRequest(
                "editMessageText",
                chat_id=chat_id,
                message_id=message_id,
                text="Пожалуйста выберите пиццу",
                reply_markup=pizza_keyboard,
            )
        return HandlerStatus.STOP
