import json
import urllib.request
from os import getenv


# Метод getUpdates запрашивает данные с сервера
# offset - параметр метода getUpdates, можно посмотреть в доке TG Bot API
# https://core.telegram.org/bots/api
def getUpdates(offset: int) -> dict:
    # Создает объект запроса, но сам запрос ещё не отправлен, указывает куда будем отправлять запрос
    request = urllib.request(
        # Метод запроса
        method="POST",
        # url-адрес (бот в данном случае). Отправляем на него getUpdates
        url=f'{getenv("BOT_TOKEN_URI")/getUpdates}',
        # Какие данные отправляются
        data={"offset": offset},
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


# sendMessage принимает сообщения которые отправлены в бота
# так же принимает аргументами параметры для sendMessage
def sendMessage(chat_id: int, text: str) -> dict:
    # Создает объект запроса, но сам запрос ещё не отправлен, указывает куда будем отправлять запрос
    request = urllib.request(
        # Метод запроса
        method="POST",
        # url-адрес (бот в данном случае). Отправляем на него sendMessage
        url=f'{getenv("BOT_TOKEN_URI")/sendMessage}',
        # Какие данные отправляются
        data={"chat_id": chat_id, "text": text},
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
