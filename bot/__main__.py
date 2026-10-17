# Основной файл запускающий бота
import asyncio

from bot.dispatcher import Dispatcher
from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers import get_handlers
from bot.infrastructure.messanger_telegram import MessengerTelegram
from bot.infrastructure.storage_postgres import StoragePostgres
from bot.long_pollin import start_long_polling


async def main() -> None:
    storage: Storage = StoragePostgres()
    messenger: Messenger = MessengerTelegram()

    try:
        dispatcher = Dispatcher(storage, messenger)
        dispatcher.add_handler(*get_handlers())
        await start_long_polling(dispatcher, messenger)
    except KeyboardInterrupt:
        print("\nБот выключен.")
    finally:
        # Закрываем соедиение при завершении
        if hasattr(messenger, "close"):
            await messenger.close()
        if hasattr(storage, "close"):
            await storage.close()


if __name__ == "__main__":
    asyncio.run(main())
