# Отправляем фото обратно пользователю

from bot.handlers.handler import Handler, HandlerStatus
import bot.telegram_client


class PhotoEcho(Handler):
    def can_handle(self, update: dict) -> bool:
        # Проверяет и возвращает, что message есть update
        # и что photo есть в message
        return "message" in update and "photo" in update["message"]

    def handle(self, update: dict) -> bool:
        # В update получаем сообщение, фото,
        # качество(оно в виде списка, поэтому -1) и id файла
        file_id = update["message"]["photo"][-1]["file_id"]
        bot.telegram_client.sendPhoto(
            chat_id=update["message"]["chat"]["id"],
            photo=file_id,
        )
        return HandlerStatus.STOP
