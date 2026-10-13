import json
import urllib.error

from bot.domain.messenger import Messenger
from bot.domain.order_state import OrderState
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


# Исправили: Переименовали класс, чтобы избежать дублирования
class SuccessfulPayment(Handler):
    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        if "message" not in update:
            return False

        return "successful_payment" in update["message"]

    def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["message"]["from"]["id"]
        chat_id = update["message"]["chat"]["id"]
        message_id = update["message"]["message_id"]
        successful_payment = update["message"]["successful_payment"]

        # Удаляем старый инвойс, чтобы кнопка оплаты исчезла из чата
        try:
            messenger.deleteMessage(chat_id=chat_id, message_id=message_id)
        except urllib.error.HTTPError:
            pass

        # ИСПРАВЛЕНО: Полностью убрали json.loads!
        # !!ВАЖНО!! УБРАННО Т.К ИСПОЛЬЗУЮ ТГ ЗВЕЗДЫ, ПРИ ОПЛАТЕ ЧЕРЕЗ ЮКАССУ И Т.П
        # СТОИТ ИСПОЛЬЗОВАТЬ json.loads и json.dumps
        # Просто берём чистую строку и разбиваем её по двоеточиям
        invoice_payload = successful_payment["invoice_payload"]
        payload_parts = invoice_payload.split(":")

        # Индексы: 0 = telegram_id, 1 = pizza_code, 2 = size_code, 3 = drink_code
        raw_pizza = payload_parts[1] if len(payload_parts) > 1 else "margherita"
        raw_size = payload_parts[2] if len(payload_parts) > 2 else "M"
        raw_drink = payload_parts[3] if len(payload_parts) > 3 else "none"

        # Справочники для расшифровки кодов обратно в русский текст
        pizza_mapping = {
            "margherita": "Маргарита",
            "pepperoni": "Пепперони",
            "quatro": "Четыре сыра",
            "capricciosa": "Капричоза",
            "diavola": "Дьявола",
            "prosciutto": "Прошутто",
        }

        pizza_size_mapping = {
            "S": "Маленькая (25см)",
            "M": "Средняя (30см)",
            "L": "Большая (35см)",
            "XL": "Очень большая (40см)",
        }

        drink_mapping = {
            "cola": "Coca-Cola",
            "fanta": "Fanta",
            "pepsi": "Pepsi",
            "7_up": "7-Up",
            "water": "Вода",
            "none": "Без напитка",
        }

        # Восстанавливаем русский текст для чека
        pizza_name = pizza_mapping.get(raw_pizza, "Маргарита")
        pizza_size = pizza_size_mapping.get(raw_size, "Средняя (30см)")
        drink_name = drink_mapping.get(raw_drink, "Без напитка")

        # Переводим пользователя в финальный стейт и очищаем его текущую корзину
        storage.update_user_state(telegram_id, OrderState.ORDER_FINISHED)
        storage.clear_user_state_and_order(telegram_id)

        # Формируем красивый текст чека
        order_information = (
            "<b>✅ Заказ успешно оплачен и принят!</b>\n\n"
            "<b>📋 Детали вашего заказа:</b>\n"
            f"🍕 Пицца: {pizza_name}\n"
            f"📐 Размер: {pizza_size}\n"
            f"🥤 Напиток: {drink_name}\n\n"
            "<i>🤩 Спасибо за заказ! Ваша пицца уже отправлена в печь. Ожидайте курьера!</i>"
        )

        # Отправляем финальное сообщение
        messenger.sendMessage(
            chat_id=chat_id,
            text=order_information,
            parse_mode="HTML",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {
                                "text": "🍕 Сделать новый заказ",
                                "callback_data": "new_order",
                            }
                        ]
                    ]
                }
            ),
        )

        return HandlerStatus.STOP
