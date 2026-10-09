# Вынесли в отдельный файл работу long_polling

from bot.dispatcher import Dispatcher
import bot.telegram_client
import time


# Принимает диспатчер
def start_long_polling(dispatcher: Dispatcher) -> None:
    next_update_offset = 0
    while True:
        # Вызывает getUpdate
        ## Явно указывает что передаем в переменную
        updates = bot.telegram_client.getUpdates(offset=next_update_offset)
        # Проходитт по всем update
        for update in updates:
            # Строка прибавляет к ID сообщения +1, чтобы не отображались старые СМС
            ## Высчитывает offset
            next_update_offset = max(next_update_offset, update["update_id"] + 1)
            # Вызываем диспатчер и говорит ему обрабатывать update
            dispatcher.dispatch(update)
            print(".", end="", flush=True)

        time.sleep(1)
