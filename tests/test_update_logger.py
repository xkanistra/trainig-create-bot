# Тестирования обновления данных пользователя

from bot.dispatcher import Dispatcher
from bot.handlers.update_database_logger import UpdateDatabaseLogger
from tests.mocks import Mock


def test_update_database_logger_executed():
    test_update = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 12345,
                "is_bot": False,
                "first_name": "test",
                "username": "testuser",
                "language_code": "ru",
            },
            "chat": {
                "id": 12345,
                "first_name": "test",
                "username": "testuser",
                "type": "private",
            },
            "date": 1791741212,
            "text": "This test message",
        },
    }

    # Булево значение нужно для имитации работы хендлера
    persist_update_called = False

    # Проверка что объект такой же что и тестовый и что он вызывается
    def persist_updates(update: list) -> None:
        nonlocal persist_update_called
        persist_update_called = True
        assert update[0] == test_update

    def get_user(telegram_id: int) -> dict | None:
        assert telegram_id == 12345
        return None

    mock_storage = Mock(
        {
            "persist_updates": persist_updates,
            "get_user": get_user,
        }
    )
    mock_messenger = Mock({})

    # Создаем логику работы main в боте но с тестовыми данными
    dispatcher = Dispatcher(mock_storage, mock_messenger)
    update_logger = UpdateDatabaseLogger()
    dispatcher.add_handler(update_logger)
    dispatcher.dispatch(test_update)

    assert persist_update_called
