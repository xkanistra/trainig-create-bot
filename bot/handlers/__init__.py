# Переменная которая содержит в себе все хендлеры
# упрощает откладку кода

from bot.handlers.back_handler import Back
from bot.handlers.ensure_users_exists import EnsureUsersExists
from bot.handlers.handler import Handler
from bot.handlers.message_start import MessageStart
from bot.handlers.order_cancel import OrderCancel
from bot.handlers.order_cofirm import OrderConfirm
from bot.handlers.pizza_selection import PizzaSelection
from bot.handlers.pizza_size import PizzaSize
from bot.handlers.pre_checkout_query import PreCheckoutQuery
from bot.handlers.successful_payment import SuccessfulPayment
from bot.handlers.update_database_logger import UpdateDatabaseLogger
from bot.handlers.wait_for_order import WaitForOrder


def get_handlers() -> list[Handler]:
    return [
        UpdateDatabaseLogger(),
        EnsureUsersExists(),
        Back(),
        PizzaSelection(),
        MessageStart(),
        PizzaSize(),
        WaitForOrder(),
        PreCheckoutQuery(),
        SuccessfulPayment(),
        OrderConfirm(),
        OrderCancel(),
    ]
