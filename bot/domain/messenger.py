# Создаем интерфейс для мессенджера
from abc import ABC, abstractmethod


class Messenger(ABC):
    @abstractmethod
    def makeRequest(self, method: str, **param) -> dict: ...

    @abstractmethod
    def getUpdates(self, **params) -> dict: ...

    @abstractmethod
    def sendMessage(self, chat_id: int, text: str, **params) -> dict: ...

    @abstractmethod
    def getMe(self) -> dict: ...

    @abstractmethod
    def deleteMessage(self, chat_id: int, message_id: int) -> dict: ...

    @abstractmethod
    def answerCallbackQuery(self, callback_query_id: str, **kwargs) -> dict: ...

    @abstractmethod
    def sendInvoice(
        self,
        chat_id: int,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        currency: str,
        prices: list,
        **kwargs
    ): ...
