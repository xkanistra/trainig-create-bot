# Основной файл запускающий бота

from bot.dispatcher import Dispatcher
from bot.handlers import message_echo
from bot.long_pollin import start_long_polling

if __name__ == "__main__":
    try:
        dispatcher = Dispatcher()
        dispatcher.add_handler(message_echo.MessageEcho())
        start_long_polling(dispatcher)
    except KeyboardInterrupt:
        print("\nБот выключен.")
