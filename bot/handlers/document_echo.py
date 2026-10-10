# Отправляем файл обратно пользователю

from bot.handlers.handler import Handler
import bot.telegram_client


class DocumentEcho(Handler):
    def can_handle(self, update: dict) -> bool:
        # Проверяет и возвращает, что message есть update
        # и что document есть в message
        return "message" in update and "document" in update["message"]

    def handle(self, update: dict) -> bool:
        # В update получаем сообщение, документ и его id
        file_id = update["message"]["document"]["file_id"]
        bot.telegram_client.sendDocument(
            chat_id=update["message"]["chat"]["id"],
            document=file_id,
        )
        return False
