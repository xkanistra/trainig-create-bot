# Тест вызова стартового сообщения с выбором пиццы


from bot.dispatcher import Dispatcher
from bot.handlers.message_start import MessageStart
from tests.mocks import Mock


def test_message_start_handler():
    test_callback_update = {
        "update_id": 987654321,
        "callback_query": {
            "id": "1020304050",
            "from": {
                "id": 1,  # Идентификатор пользователя при клике
                "is_bot": False,
                "first_name": "test",
                "username": "test_user",
                "language_code": "ru",
            },
            "message": {
                "message_id": 1,
                "from": {
                    "id": 4321,
                    "is_bot": True,
                    "first_name": "testBot",
                    "username": "testuser_bot",
                },
                "chat": {
                    "id": 123456789,
                    "first_name": "test",
                    "username": "test_user",
                    "type": "private",
                },
                "date": 1791741475,
                "edit_date": 1791802866,
                "text": "Test callback",
                "reply_markup": {
                    "inline_keyboard": [
                        [
                            {
                                "text": "Сделать новый заказ",
                                "callback_data": "new_order",
                            }
                        ]
                    ]
                },
            },
            "chat_instance": "-299958882809016784",
            "data": "new_order",
        },
    }

    test_message_update = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 4321,  # Идентификатор пользователя при тексте
                "is_bot": False,
                "first_name": "test",
                "username": "test_user",
                "language_code": "ru",
            },
            "chat": {
                "id": 123456789,
                "first_name": "test",
                "username": "test_user",
                "type": "private",
            },
            "date": 1791741475,
            "text": "/start",
            "entities": [{"offset": 0, "length": 6, "type": "bot_command"}],
        },
    }

    clear_user_state_and_order_called = 0
    update_user_state_called = 0

    def clear_user_state_and_order(telegram_id: int) -> None:
        assert telegram_id in [4321, 1]
        nonlocal clear_user_state_and_order_called
        clear_user_state_and_order_called += 1

    def update_user_state(telegram_id: int, state: str) -> None:
        assert telegram_id in [4321, 1]
        assert state == "WAIT_FOR_PIZZA_NAME"
        nonlocal update_user_state_called
        update_user_state_called += 1

    def get_user(telegram_id: int) -> dict | None:
        assert telegram_id in [4321, 1]
        return {"state": None, "order_json": "{}"}

    message_calls = []

    def sendMessage(chat_id: int, text: str, **params) -> dict:
        assert chat_id == 123456789
        message_calls.append({"text": text, "params": params})
        return {"ok": True}

    def answerCallbackQuery(callback_query_id: str, **kwargs) -> dict:
        assert callback_query_id == "1020304050"
        return {"ok": True}

    make_request_called = False

    def makeRequest(method: str, **param) -> dict:
        assert method == "editMessageText"
        assert param["chat_id"] == 123456789
        nonlocal make_request_called
        make_request_called = True
        return {"ok": True}

    mock_storage = Mock(
        {
            "clear_user_state_and_order": clear_user_state_and_order,
            "update_user_state": update_user_state,
            "get_user": get_user,
        }
    )

    mock_messenger = Mock(
        {
            "sendMessage": sendMessage,
            "answerCallbackQuery": answerCallbackQuery,
            "makeRequest": makeRequest,
        }
    )

    # Создаем логику работы main в боте но с тестовыми данными
    dispatcher = Dispatcher(mock_storage, mock_messenger)
    message_start = MessageStart()
    dispatcher.add_handler(message_start)
    dispatcher.dispatch(test_message_update)
    dispatcher.dispatch(test_callback_update)

    assert clear_user_state_and_order_called == 2
    assert update_user_state_called == 2
    assert len(message_calls) == 2
    assert make_request_called == True
