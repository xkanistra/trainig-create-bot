# Хендлер записывает информацию в БД


from bot.handler import Handler
import bot.database_client


class PresistUpdates(Handler):
    def can_handle(self, update: dict) -> bool:
        # Возвращает True при любом типе данных
        return True

    def handle(self, update: dict) -> bool:
        # Записыва все полученные данные в БД и возвращаем True, чтобы
        # перешло к другому хендлеру
        bot.database_client.persist_updates([update])
        return True
