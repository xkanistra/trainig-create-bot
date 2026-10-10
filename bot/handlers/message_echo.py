# Создаем хендлеры

from bot.handlers.handler import Handler, HandlerStatus
import bot.telegram_client


class MessageEcho(Handler):
    def can_handle(self, update: dict) -> bool:
        # Проверяет и возвращает, что message есть update
        # и что text есть в message
        return "message" in update and "text" in update["message"]

    # try/except не ставим, т.к can_handle гарантирует что придет message и text
    def handle(self, update: dict) -> bool:
        bot.telegram_client.sendMessage(
            chat_id=update["message"]["chat"]["id"],
            text=update["message"]["text"],
        )
        return HandlerStatus.STOP


# После написания хендлера нужно внести его в архитектуру бота в __main__.py
