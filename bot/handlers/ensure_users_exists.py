import bot.database_client
from bot.handlers.handler import Handler, HandlerStatus


class EnsureUsersExists(Handler):
    def can_handle(self, update: dict) -> bool:
        # Проверяет message на наличие from, т.к в from хранится ID
        return "message" in update and "from" in update["message"]

    def handle(self, update: dict) -> bool: 
        # В update получаем сообщение, документ и его id
        telegram_id = update["message"]["from"]["id"]
        bot.database_client.ensure_users_exists(telegram_id)
        return HandlerStatus.CONTINUE
