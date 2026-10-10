# Написание диспетчера


from bot.handlers.handler import Handler
from bot.tools.json_inspector import inspect


class Dispatcher:
    def __init__(self):
        # Создаем массив хендлеров
        self.__handlers: list[Handler] = []

    # Метод добавляет хендлеры в массив
    def add_handler(self, *handlers: list[Handler]) -> None:
        for handler in handlers:
            self.__handlers.append(handler)

    # Метод обрабатывает сигнал из хендлера
    def dispatch(self, update: dict) -> None:
        inspect(update)
        # Перебирает массив
        for handler in self.__handlers:
            # Если хендлер говорит что он все сделал,
            # останавливаем перебор хендлеров
            if handler.can_handle(update):
                signal = handler.handle(update)
                if not signal:
                    break
