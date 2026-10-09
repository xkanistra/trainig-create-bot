# Создаем класс Handler с абрстактным классом abs
from abc import ABC, abstractmethod


class Handler(ABC):
    # @ это декораторы
    @abstractmethod
    def can_handle(self, update: dict) -> bool: ...

    @abstractmethod
    def handle(self, update: dict) -> bool:
        """_summary_
        return options
        - true - signal for dispatcher to continue processing
        - false - signal for dispatcher to stop processing
        """
