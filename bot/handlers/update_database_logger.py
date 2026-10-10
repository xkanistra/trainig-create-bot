# Хендлер записывает информацию в БД

from bot.handlers.handler import Handler, HandlerStatus
import bot.database_client


class UpdateDatabaseLogger(Handler):
    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        # Возвращает True при любом типе данных
        return True

    def handle(self, update: dict, state: str, order_json: dict) -> HandlerStatus:
        # Записыва все полученные данные в БД и возвращаем True, чтобы
        # перешло к другому хендлеру
        bot.database_client.persist_updates([update])
        return HandlerStatus.CONTINUE
