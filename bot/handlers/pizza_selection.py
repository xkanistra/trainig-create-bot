# Хендлер обрабатывает нажатие выбора пиццы

import asyncio
import json

import httpx
from bot.domain.messenger import Messenger
from bot.domain.order_state import OrderState
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class PizzaSelection(Handler):
    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        # Если нету callback в update, вернуть False
        if "callback_query" not in update:
            return False

        # Если состояние из которого пришел callback, состояние достает dispatch из БД
        # не равен выбору названия пиццы вернуть False
        if state != OrderState.WAIT_FOR_PIZZA_NAME:
            return False

        # Достаем данные о пиццах, в дате будет название из callback_data
        # в message_start.py
        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("pizza_")

    async def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        # Достаем telegram_id и callback_data из update. Они точно есть т.к can_handle это проверяет
        telegram_id = update["callback_query"]["from"]["id"]
        chat_id = update["callback_query"]["message"]["chat"]["id"]
        message_id = update["callback_query"]["message"]["message_id"]

        callback_data = update["callback_query"]["data"]

        # Добавляем маппинг по имени для красивого вывода в БД
        name_mapping = {
            "pizza_margherita": "Маргарита",
            "pizza_pepperoni": "Пепперони",
            "pizza_quatro_stagioni": "Четыре сыра",
            "pizza_capricciosa": "Капричоза",
            "pizza_diavola": "Дьявола",
            "pizza_prosciutto": "Прошутто",
        }

        # Добавляем переменные для явного четния кода
        pizza_name = name_mapping.get(callback_data)
        order_json["pizza_name"] = pizza_name

        # Блок обновляет состояние и добавляет название заказываемой пиццы
        await asyncio.gather(
            storage.update_user_order_json(telegram_id, order_json),
            storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_SIZE),
        )

        try:
            # Данная строка убирает визуальное колесо загрузки
            await messenger.answerCallbackQuery(update["callback_query"]["id"])
        except httpx.HTTPStatusError:
            pass
        
        await messenger.makeRequest(
            "editMessageText",
            chat_id=chat_id,
            message_id=message_id,
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
                        [
                            {"text": "⬅️ Назад", "callback_data": "back_to_pizza_name"},
                        ],
                    ]
                }
            ),
        )
        return HandlerStatus.STOP
