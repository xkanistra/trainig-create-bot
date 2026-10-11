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

        # Установка дефолтных состояний на случай краша БД
        pizza_name = "Не выбрана"
        pizza_size = "Не выбран"
        drink_name = "Не выбран"

        # Берем данные о заказе
        order = bot.database_client.get_order_json(telegram_id)

        # Записываем данные о заказе для дальнейшего вывода
        if order:
            pizza_name = order.get("pizza_name", "Не выбрана")
            pizza_size = order.get("pizza_size", "Не выбран")
            drink_name = order.get("drink_name", "Не выбран")

        drink_mapping = {
            "drink_coca_cola": "Coca-Cola",
            "drink_fanta": "Fanta",
            "drink_pepsi": "Pepsi",
            "drink_7_up": "7-Up",
            "drink_water": "Вода",
            "drink_none": "Без напитка",
        }

        drink_name = drink_mapping.get(callback_data)
        order_json["drink_name"] = drink_name

        bot.database_client.update_user_order_json(telegram_id, order_json)
        bot.database_client.update_user_state(telegram_id, "WAIT_FOR_ORDER")

        try:
            bot.telegram_client.answerCallbackQuery(update["callback_query"]["id"])
        except Exception:
            pass

        bot.telegram_client.makeRequest(
            "editMessageText",
            chat_id=chat_id,
            message_id=message_id,
            text=f"Подтвердите ваш заказ:\nПицца: {pizza_name}\nРазмер: {pizza_size}\nНапиток: {drink_name}",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {
                                "text": "✅ Всё верно, заказываю!",
                                "callback_data": "confirm_order",
                            },
                            {
                                "text": "❌ Отменить заказ",
                                "callback_data": "cancel_order",
                            },
                        ],
                        [
                            {"text": "⬅️ Назад", "callback_data": "back_to_drink"},
                        ],
                    ]
                }
            ),
        )
        return HandlerStatus.STOP
