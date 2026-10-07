import json
import urllib.request
from os import getenv


# Функцией фиксим дублирование кода
# method - принимает любые методы для объектов
# **param передает любой набор параметров, благодаря **
def makeRequest(method: str, **param) -> dict:
    # Строкой заменяем переменную data в строках 26, 50 и т.п.
    json_data = json.dumps(param).encode("utf-8")
    # Создает объект запроса, но сам запрос ещё не отправлен, указывает куда будем отправлять запрос
    request = urllib.request(
        # Метод запроса
        method="POST",
        # url-адрес (бот в данном случае). Отправляем на него getUpdates/sendMessage и т.п через method
        url=f'{getenv("BOT_TOKEN_URI")/{method}}',
        # Какие данные отправляются
        data=json_data,
        # Какой тип данных
        headers={"Content-Type": "application/json"},
    )

    # Как отправить данные. Работает так же как и на открытие файлов (сам закрывает, не нужен closed)
    # В respone храниться ответ на наш запрос, как при открытии файла, мы помещаем данные в переменную
    with urllib.request.urlopen(request) as response:
        # Получаем тело ответа, для этого:
        # методом read читаем ответ, методом decode декодируем в utf-8
        response_body = response.read().decode("utf-8")
        # Получаем json ответ
        response_json = json.loads(response_body)
        # Возвращаем ответ
        return response_json["result"]


# Метод getUpdates запрашивает данные с сервера
# offset - параметр метода getUpdates, можно посмотреть в доке TG Bot API
# https://core.telegram.org/bots/api
def getUpdates(offset: int) -> dict:
    # Используем новую функцию для создания универсальных запросов
    return makeRequest("getUpdates", offset=offset)


# sendMessage принимает сообщения которые отправлены в бота
# так же принимает аргументами параметры для sendMessage
def sendMessage(chat_id: int, text: str) -> dict:
    return makeRequest("sendMessage", chat_id=chat_id, text=text)


# getMe способ тестирования токена аутентификации вашего бота. Не требуется никаких параметров
def getMe() -> dict:
    return makeRequest("getMe")
