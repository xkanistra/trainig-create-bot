# Создаем интерфейс для мессенджера
from abc import ABC, abstractmethod


class Messenger(ABC):
    @abstractmethod
    async def makeRequest(self, method: str, **param) -> dict: ...

    @abstractmethod
    async def getUpdates(self, **params) -> dict: ...

    @abstractmethod
    async def sendMessage(self, chat_id: int, text: str, **params) -> dict: ...

    @abstractmethod
    async def getMe(self) -> dict: ...

    @abstractmethod
    async def deleteMessage(self, chat_id: int, message_id: int) -> dict: ...

    @abstractmethod
    async def answerCallbackQuery(self, callback_query_id: str, **kwargs) -> dict: ...

    @abstractmethod
    async def sendInvoice(
        self,
        chat_id: int,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        currency: str,
        prices: list,
        **kwargs
    ) -> dict: ...

    @abstractmethod
    async def answerPreCheckoutQuery(
        pre_checkout_query_id: str, ok: bool, **kwargs
    ) -> dict: ...
