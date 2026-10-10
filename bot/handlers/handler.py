# Создаем класс Handler с абрстактным классом abs
## Изменение логики хендлера
from abc import ABC, abstractmethod

# Enum позволяет создавать именнованные константы с уникальными именами изначениями
from enum import Enum


# Класс отображает состояние обработки
class HandlerStatus(Enum):
    CONTINUE = 1
    STOP = 2


class Handler(ABC):
    # @ это декораторы
    @abstractmethod
    def can_handle(self, update: dict) -> bool: ...

    # Возвращает константы. 
    # CONTINUE - переход к след. хендлеру
    # STOP - остановка обработки update
    @abstractmethod
    def handle(self, update: dict) -> HandlerStatus: ...
