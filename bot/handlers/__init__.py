# Переменная которая содержит в себе все хендлеры
# упрощает откладку кода

from bot.handlers.ensure_users_exists import EnsureUsersExists
from bot.handlers.handler import Handler
from bot.handlers.message_start import MesageStart
from bot.handlers.pizza_selection import PizzaSelection
from bot.handlers.update_database_logger import UpdateDatabaseLogger


def get_handlers() -> list[Handler]:
    return [
        UpdateDatabaseLogger(),
        EnsureUsersExists(),
        MesageStart(),
        PizzaSelection()
    ]
