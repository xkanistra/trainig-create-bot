# Хендлер отправляет сообщ при входе пользователя

import json
import bot.telegram_client
import bot.database_client
from bot.handlers.handler import Handler, HandlerStatus


class MesageStart(Handler):
    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        # Проверяет сообщение что оно text и что text /start
        return (
            "message" in update
            and "text" in update["message"]
            and update["message"]["text"] == "/start"
        )

    def handle(self, update: dict, state: str, order_json: dict) -> bool:
        # В update получаем сообщение, документ и его id
        telegram_id = update["message"]["from"]["id"]

        # Очищает заказ клиента
        bot.database_client.clear_user_state_and_order(telegram_id)
        bot.database_client.update_user_state(telegram_id, "WAIT_FOR_PIZZA_NAME")

        # Блок удаляет любую клавиатуру помимо Inline
        bot.telegram_client.sendMessage(
            chat_id=update["message"]["chat"]["id"],
            text="Добро пожаловать в Пиццерию!",
            reply_markup=json.dumps({"remove_keyboard": True}),
        )

        bot.telegram_client.sendMessage(
            chat_id=update["message"]["chat"]["id"],
            text="Пожалуйста выбери пиццу",
            reply_markup=json.dumps(
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
                    ]
                }
            ),
        )
        return HandlerStatus.STOP
