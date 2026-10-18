# Хендлер отправляет сообщ при входе пользователя
import json

import httpx

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
        # Сценарий 1: Текстовая команда /start
        if (
            "message" in update
            and "text" in update["message"]
            and update["message"]["text"] == "/start"
        ):
            return True

        # Сценарий 2: Нажатие кнопки нового заказа (в том числе после оплаты или отмены)
        if "callback_query" in update:
            return update["callback_query"]["data"] == "new_order"

        return False

    async def handle(
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
        await storage.clear_user_state_and_order(telegram_id)
        await storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_NAME)

        if message_command:
            # Сценарий А: Текстовый /start -> строго отправляем НОВЫЕ сообщения. Обрабатываем асинхронно
            await messenger.sendMessage(
                chat_id=chat_id,
                text="Добро пожаловать в Пиццерию!",
                reply_markup=json.dumps({"remove_keyboard": True}),
            )
            await messenger.sendMessage(
                chat_id=chat_id,
                text="Пожалуйста выберите пиццу",
                reply_markup=pizza_keyboard,
            ),

        else:
            # Сценарий Б: Нажата инлайн-кнопка -> обрабатываем логику перерисовки интерфейса
            try:
                await messenger.answerCallbackQuery(update["callback_query"]["id"])
            except httpx.HTTPStatusError:
                pass

            # Если мы отменяем заказ с экрана инвойса, удаляем его и шлем новое меню
            if state == OrderState.ORDER_CONFIRM:
                try:
                    await messenger.deleteMessage(
                        chat_id=chat_id, message_id=message_id
                    ),
                except httpx.HTTPStatusError:
                    pass

                messenger.sendMessage(
                    chat_id=chat_id,
                    text="Пожалуйста выберите пиццу",
                    reply_markup=pizza_keyboard,
                )
            # В остальных случаях (кнопка под чеком успешной оплаты) плавно редактируем текст
            else:
                try:
                    await messenger.makeRequest(
                        "editMessageText",
                        chat_id=chat_id,
                        message_id=message_id,
                        text="Пожалуйста выберите пиццу",
                        reply_markup=pizza_keyboard,
                    )
                except httpx.HTTPStatusError:
                    pass

        return HandlerStatus.STOP
