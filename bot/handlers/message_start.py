# Хендлер отправляет сообщ при входе пользователя

import json
import bot.telegram_client
import bot.database_client
from bot.handlers.handler import Handler, HandlerStatus


class MesageStart(Handler):
    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        # Проверяем условия при отправке смс, что отбросит любой шанс сломать бота смс
        if (
            "message" in update
            and "text" in update["message"]
            and update["message"]["text"] == "/start"
        ):
            return True

        if "callback_query" in update and update["callback_query"]["data"].startswith("new_"):
            return True

        return False

    def handle(self, update: dict, state: str, order_json: dict) -> HandlerStatus:
        # Фильтруем приходящее сообщение, либо это /start либо callback и исходя из этого берем данные
        if "callback_query" not in update:
            telegram_id = update["message"]["from"]["id"]
            chat_id = update["message"]["chat"]["id"]
        else:
            telegram_id = update["callback_query"]["from"]["id"]
            chat_id = update["callback_query"]["message"]["chat"]["id"]
            message_id = update["callback_query"]["message"]["message_id"]

        # Очищает заказ клиента
        bot.database_client.clear_user_state_and_order(telegram_id)
        bot.database_client.update_user_state(telegram_id, "WAIT_FOR_PIZZA_NAME")

        try:
            bot.telegram_client.answerCallbackQuery(update["callback_query"]["id"])
        except Exception:
            pass

        if (
            "message" in update
            and "text" in update["message"]
            and update["message"]["text"] == "/start"
        ):
            # Блок удаляет любую клавиатуру помимо Inline
            bot.telegram_client.sendMessage(
                chat_id=update["message"]["chat"]["id"],
                text="Добро пожаловать в Пиццерию!",
                reply_markup=json.dumps({"remove_keyboard": True}),
            )

            bot.telegram_client.sendMessage(
                chat_id=chat_id,
                text="Пожалуйста выберите пиццу",
                reply_markup=json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "Маргарита",
                                    "callback_data": "pizza_margherita",
                                },
                                {
                                    "text": "Пепперони",
                                    "callback_data": "pizza_pepperoni",
                                },
                            ],
                            [
                                {
                                    "text": "Четыре сыра",
                                    "callback_data": "pizza_quatro_stagioni",
                                },
                                {
                                    "text": "Капричоза",
                                    "callback_data": "pizza_capricciosa",
                                },
                            ],
                            [
                                {"text": "Дьявола", "callback_data": "pizza_diavola"},
                                {
                                    "text": "Прошутто",
                                    "callback_data": "pizza_prosciutto",
                                },
                            ],
                        ],
                    },
                ),
            )
        else:
            try:
                bot.telegram_client.answerCallbackQuery(update["callback_query"]["id"])
            except Exception:
                pass
            bot.telegram_client.makeRequest(
                "editMessageText",
                chat_id=chat_id,
                message_id=message_id,
                text="Пожалуйста выберите пиццу",
                reply_markup=json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "Маргарита",
                                    "callback_data": "pizza_margherita",
                                },
                                {
                                    "text": "Пепперони",
                                    "callback_data": "pizza_pepperoni",
                                },
                            ],
                            [
                                {
                                    "text": "Четыре сыра",
                                    "callback_data": "pizza_quatro_stagioni",
                                },
                                {
                                    "text": "Капричоза",
                                    "callback_data": "pizza_capricciosa",
                                },
                            ],
                            [
                                {"text": "Дьявола", "callback_data": "pizza_diavola"},
                                {
                                    "text": "Прошутто",
                                    "callback_data": "pizza_prosciutto",
                                },
                            ],
                        ]
                    }
                ),
            )
        return HandlerStatus.STOP
