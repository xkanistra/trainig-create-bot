# Вынесли в отдельный файл работу long_polling

import time

from bot.dispatcher import Dispatcher
from bot.domain.messenger import Messenger


# Принимает диспатчер
def start_long_polling(dispatcher: Dispatcher, messenger: Messenger) -> None:
    next_update_offset = 0
    while True:
        # Вызывает getUpdate
        ## Явно указывает что передаем в переменную
        ### UPD. Указываем какие обновления хотим получать в allowed_updates
        updates = messenger.getUpdates(
            offset=next_update_offset, allowed_updates=["message", "callback_query", "pre_checkout_query"]
        )
        # Проходитт по всем update
        for update in updates:
            # Строка прибавляет к ID сообщения +1, чтобы не отображались старые СМС
            ## Высчитывает offset
            next_update_offset = max(next_update_offset, update["update_id"] + 1)
            # Вызываем диспатчер и говорит ему обрабатывать update
            dispatcher.dispatch(update)
            print(".", end="", flush=True)

        time.sleep(1)
