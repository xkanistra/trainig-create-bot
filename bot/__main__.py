# Основной файл запускающий бота
from bot.dispatcher import Dispatcher
from bot.handlers import document_echo, message_echo, photo_echo, update_database_logger
from bot.long_pollin import start_long_polling

if __name__ == "__main__":
    try:
        dispatcher = Dispatcher()
        dispatcher.add_handler(update_database_logger.PresistUpdates())
        dispatcher.add_handler(message_echo.MessageEcho())
        dispatcher.add_handler(photo_echo.PhotoEcho())
        dispatcher.add_handler(document_echo.DocumentEcho())
        start_long_polling(dispatcher)
    except KeyboardInterrupt:
        print("\nБот выключен.")
