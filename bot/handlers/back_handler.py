# Хендлер обрабатывает нажатие кнопки назад

import json

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class Back(Handler):
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

        # Достаем данные о пиццах, в дате будет название из callback_data
        # в message_start.py
        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("back_")

    def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        # Достаем данные для управления дальнейшего сообщением через метод editMessageText отправленный в makeRequest
        telegram_id = update["callback_query"]["from"]["id"]
        chat_id = update["callback_query"]["message"]["chat"]["id"]
        message_id = update["callback_query"]["message"]["message_id"]

        callback_data = update["callback_query"]["data"]

        messenger.answerCallbackQuery(update["callback_query"]["id"])

        next_text = ""
        next_keyboard = []

        if callback_data == "back_to_pizza_name":
            # Возвращаем состояние с выбора размера на выбор пиццы
            storage.update_user_state(telegram_id, "WAIT_FOR_PIZZA_NAME")

            # Очищаем заказ т.к вернулись в самое начало
            if "pizza_name" in order_json:
                del order_json["pizza_name"]
                storage.update_user_order_json(telegram_id, order_json)

            next_text = "Выберите пиццу (Вы вернулись назад)"
            next_keyboard = [
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

        elif callback_data == "back_to_pizza_size":
            # Возвращаем состояние с выбора размера на выбор пиццы
            storage.update_user_state(telegram_id, "WAIT_FOR_PIZZA_SIZE")

            # Очищаем заказ т.к вернулись в самое начало
            if "pizza_size" in order_json:
                del order_json["pizza_size"]
                storage.update_user_order_json(telegram_id, order_json)

            next_text = "Выберите размер пиццы (Вы вернулись назад)"
            next_keyboard = [
                [
                    {"text": "Маленькая (25см)", "callback_data": "size_small"},
                    {"text": "Средняя (30см)", "callback_data": "size_medium"},
                ],
                [
                    {"text": "Большая (35см)", "callback_data": "size_large"},
                    {"text": "Очень большая (40см)", "callback_data": "size_xl"},
                ],
                [
                    {"text": "⬅️ Назад", "callback_data": "back_to_pizza_name"},
                ],
            ]

        elif callback_data == "back_to_drink":
            # Возвращаем состояние с выбора размера на выбор пиццы
            storage.update_user_state(telegram_id, "WAIT_FOR_DRINKS")

            # Очищаем заказ т.к вернулись в самое начало
            if "drink_name" in order_json:
                del order_json["drink_name"]
                storage.update_user_order_json(telegram_id, order_json)

            next_text = "Выберите напиток (Вы вернулись назад)"
            next_keyboard = [
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

        # Отправляем обновленный запрос меняющий текст, а не удаляющий его и отправляющий новый
        if next_text:
            messenger.makeRequest(
                "editMessageText",
                chat_id=chat_id,
                message_id=message_id,
                text=next_text,
                reply_markup=json.dumps({"inline_keyboard": next_keyboard}),
            )

        return HandlerStatus.STOP
