# Основной файл запускающий бота
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[{asctime}.{msecs:03.0f}] {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
    force=True,
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

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

    finally:
        # Закрываем соедиение при завершении
        if hasattr(messenger, "close"):
            await messenger.close()
        if hasattr(storage, "close"):
            await storage.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот выключен.")
