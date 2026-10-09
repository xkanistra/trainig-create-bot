import json
import urllib.request
from os import getenv
from dotenv import load_dotenv

# Функция читает файл .env и загружает все данные из него в приложение
# без него не будет работать строка getenv
load_dotenv()


# Функцией фиксим дублирование кода
# method - принимает любые методы для объектов
# **param передает любой набор параметров, благодаря **
def makeRequest(method: str, **param) -> dict:
    # Строкой заменяем переменную data в строках 26, 50 и т.п.
    json_data = json.dumps(param).encode("utf-8")
    # Создает объект запроса, но сам запрос ещё не отправлен, указывает куда будем отправлять запрос
    request = urllib.request.Request(
        # Метод запроса
        method="POST",
        # url-адрес (бот в данном случае). Отправляем на него getUpdates/sendMessage и т.п через method
        url=f"{getenv('BOT_TOKEN_URI')}/{method}",
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
## UPD: Замена в запросе обновления конкретного типа данных, на любой тип данных
## Тоже самое делает в main
def getUpdates(**params) -> dict:
    # Используем новую функцию для создания универсальных запросов
    return makeRequest("getUpdates", **params)


# sendMessage принимает сообщения которые отправлены в бота
# так же принимает аргументами параметры для sendMessage
## UPD: Явно указываем что могут быть и другие параметры
def sendMessage(chat_id: int, text: str, **params) -> dict:
    return makeRequest("sendMessage", chat_id=chat_id, text=text, **params)


# getMe способ тестирования токена аутентификации вашего бота. Не требуется никаких параметров
def getMe() -> dict:
    return makeRequest("getMe")


def sendPhoto(chat_id: int, photo: str, **params) -> dict:
    return makeRequest("sendPhoto", chat_id=chat_id, photo=photo, **params)


def sendDocument(chat_id: int, document: str, **params) -> dict:
    return makeRequest("sendDocument", chat_id=chat_id, document=document, **params)