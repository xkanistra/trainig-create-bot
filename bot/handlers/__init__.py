# Переменная которая содержит в себе все хендлеры
# упрощает откладку кода

from bot.handlers.document_echo import DocumentEcho
from bot.handlers.ensure_users_exists import EnsureUsersExists
from bot.handlers.handler import Handler
from bot.handlers.message_echo import MessageEcho
from bot.handlers.photo_echo import PhotoEcho
from bot.handlers.update_database_logger import UpdateDatabaseLogger


def get_handlers() -> list[Handler]:
    return [
        UpdateDatabaseLogger(),
        EnsureUsersExists(),
        MessageEcho(),
        PhotoEcho(),
        DocumentEcho(),
    ]
