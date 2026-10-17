from bot.domain.messenger import Messenger
from bot.domain.order_state import OrderState
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class EnsureUsersExists(Handler):
    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        ## UPD. Нужно проверять наличе message и наличие callback_query
        return (
            "message" in update
            and "from" in update["message"]
            or "callback_query" in update
            and "from" in update["callback_query"]
        )

    async def handle(
        self,
        update: OrderState,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        if "message" in update:
            telegram_id = update["message"]["from"]["id"]
        else:
            telegram_id = update["callback_query"]["from"]["id"]

        await storage.ensure_users_exists(telegram_id)
        return HandlerStatus.CONTINUE
