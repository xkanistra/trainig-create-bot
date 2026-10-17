# Хендлер принимает подтверждение заказа
import asyncio
import json
import httpx

from bot.domain.messenger import Messenger
from bot.domain.order_state import OrderState
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class OrderConfirm(Handler):
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
        return callback_data.startswith("confirm_")

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

        try:
            await messenger.answerCallbackQuery(update["callback_query"]["id"])
        # Перехватываем только ошибки сети Telegram API
        except httpx.HTTPStatusError:
            pass

        pizza_name = order_json.get("pizza_name", "Пицца")
        pizza_size = order_json.get("pizza_size", "Не выбран")
        drink_name = order_json.get("drink_name", "Не выбран")

        pizza_prices = {
            ## Пока что цены будут в звездах
            "Маленькая (25см)": 1,  # 20.00 byn
            "Средняя (30см)": 2,  # 25.00 byn
            "Большая (35см)": 3,  # 30.00 byn
            "Очень большая (40см)": 4,  # 40.00 byn
        }

        drink_price = 1  # 2.00 byn

        total_amount = pizza_prices.get(pizza_size, 1)

        if drink_name and drink_name != "Без напитка":
            total_amount = total_amount + drink_price

        prices = [
            {"label": f"Заказ: Пицца + Напиток {pizza_size}", "amount": total_amount}
        ]

        # Сжимаем русские слова в короткие латинские коды (байты)
        size_code = "S"
        if "Средняя" in pizza_size:
            size_code = "M"
        elif "Большая" in pizza_size:
            size_code = "L"
        elif "Очень большая" in pizza_size:
            size_code = "XL"

        drink_code = "none"
        if "Coca-Cola" in drink_name:
            drink_code = "cola"
        elif "Fanta" in drink_name:
            drink_code = "fanta"
        elif "Pepsi" in drink_name:
            drink_code = "pepsi"
        elif "7-Up" in drink_name:
            drink_code = "7_up"
        elif "Вода" in drink_name:
            drink_code = "water"

        pizza_code = "margherita"
        if "Пепперони" in pizza_name:
            pizza_code = "pepperoni"
        elif "Четыре сыра" in pizza_name:
            pizza_code = "quatro"
        elif "Капричоза" in pizza_name:
            pizza_code = "capricciosa"
        elif "Дьявола" in pizza_name:
            pizza_code = "diavola"
        elif "Прошутто" in pizza_name:
            pizza_code = "prosciutto"

        order_payload = f"{telegram_id}:{pizza_code}:{size_code}:{drink_code}"

        try:
            await messenger.makeRequest(
                "deleteMessage", chat_id=chat_id, message_id=message_id
            )

        except httpx.HTTPStatusError:
            pass

        await messenger.makeRequest(
            "sendInvoice",
            chat_id=chat_id,
            title=f"Заказ №{update['update_id']}",
            description=f"Пицца {pizza_name}, {pizza_size}. Напиток: {drink_name}. Итого: {total_amount} ⭐",
            payload=order_payload,
            provider_token="",  # В дальнейшем подставить токен кассы
            currency="XTR",  # Валюта ТГ звезды, в дальнешем валюту страны
            prices=json.dumps(prices),
            is_flexible=False,
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [{"text": "⭐ Оплатить заказ", "pay": True}],  # Кнопка оплаты
                        [
                            {
                                "text": "❌ Отменить и начать сначала",
                                "callback_data": "new_order",
                            }
                        ],
                    ]
                }
            ),
        )
        await storage.update_user_state(telegram_id, OrderState.ORDER_CONFIRM),

        return HandlerStatus.STOP
