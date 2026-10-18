import logging
import time
from os import getenv

import httpx
from dotenv import load_dotenv

from bot.domain.messenger import Messenger

# Функция читает файл .env и загружает все данные из него в приложение
# без него не будет работать строка getenv
load_dotenv()

logger = logging.getLogger(__name__)


class MessengerTelegram(Messenger):
    def __init__(self):
        self._session: httpx.AsyncClient | None = None

    def _get_telegram_base_uri(self) -> str:
        return f"https://api.telegram.org/bot{getenv('BOT_TOKEN')}"

    def _get_telegram_file_uri(self) -> str:
        return f"https://api.telegram.org/file/bot{getenv('BOT_TOKEN')}"

    async def _get_session(self) -> httpx.AsyncClient:
        # Добавлена проверка на .is_closed на случай, если сессию закрыли, но объект остался
        if self._session is None or self._session.is_closed:
            self._session = httpx.AsyncClient(timeout=httpx.Timeout(70.0))
        return self._session

    async def makeRequest(self, method: str, **kwargs) -> dict:
        url = f"{self._get_telegram_base_uri()}/{method}"
        start_time = time.time()

        logger.info(f"[HTTP] -> POST {method}")

        try:
            session = await self._get_session()

            # В httpx запрос делается без async with
            response = await session.post(
                url,
                json=kwargs,
                headers={"Content-Type": "application/json"},
            )

            # В httpx метод .json() — синхронный (без await)
            response_json = response.json()

            # Вместо assert лучше использовать стандартный raise,
            # так как assert можно случайно отключить флагом -O при запуске Python
            if not response_json.get("ok"):
                raise ValueError(f"Telegram API error: {response_json}")

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[HTTP] <- POST {method} - {duration_ms:.2f}ms")

            return response_json["result"]

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[HTTP] X POST {method} - {duration_ms:.2f}ms - ERROR: {e}")
            raise

    async def close(self) -> None:
        # Исправлена проверка: проверяем именно self._session
        if self._session is not None and not self._session.is_closed:
            await self._session.aclose()

    # https://core.telegram.org/bots/api#getupdates
    async def getUpdates(self, **kwargs) -> dict:
        return await self.makeRequest("getUpdates", **kwargs)

    # https://core.telegram.org/bots/api#sendmessage
    async def sendMessage(self, chat_id: int, text: str, **kwargs) -> dict:
        return await self.makeRequest(
            "sendMessage", chat_id=chat_id, text=text, **kwargs
        )

    # https://core.telegram.org/bots/api#getme
    async def getMe(self) -> dict:
        return await self.makeRequest("getMe")

    # https://core.telegram.org/bots/api#deletemessage
    async def deleteMessage(self, chat_id: int, message_id: int) -> dict:
        return await self.makeRequest(
            "deleteMessage", chat_id=chat_id, message_id=message_id
        )

    # https://core.telegram.org/bots/api#answercallbackquery
    async def answerCallbackQuery(self, callback_query_id: str, **kwargs) -> dict:
        return await self.makeRequest(
            "answerCallbackQuery", callback_query_id=callback_query_id, **kwargs
        )

    # https://core.telegram.org/bots/api#sendinvoice
    async def sendInvoice(
        self,
        chat_id,
        title,
        description,
        payload,
        provider_token,
        currency,
        prices,
        **kwargs,
    ):
        return await self.makeRequest(
            "sendInvoice",
            chat_id=chat_id,
            title=title,
            description=description,
            payload=payload,
            provider_token=provider_token,
            currency=currency,
            prices=prices,
            **kwargs,
        )

    # https://core.telegram.org/bots/api#answerprecheckoutquery
    async def answerPreCheckoutQuery(
        self, pre_checkout_query_id: str, ok: bool, **kwargs
    ) -> dict:
        return await self.makeRequest(
            "answerPreCheckoutQuery",
            pre_checkout_query_id=pre_checkout_query_id,
            ok=ok,
            **kwargs,
        )
