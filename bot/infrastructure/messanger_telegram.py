import json
import urllib.request
from os import getenv

from dotenv import load_dotenv

from bot.domain.messenger import Messenger

# Функция читает файл .env и загружает все данные из него в приложение
# без него не будет работать строка getenv
load_dotenv()


class MessengerTelegram(Messenger):
    # Функцией фиксим дублирование кода
    # method - принимает любые методы для объектов
    # **param передает любой набор параметров, благодаря **
    def makeRequest(self, method: str, **param) -> dict:
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
        try:
            with urllib.request.urlopen(request) as response:
                # Получаем тело ответа, для этого:
                # методом read читаем ответ, методом decode декодируем в utf-8
                response_body = response.read().decode("utf-8")
                # Получаем json ответ
                response_json = json.loads(response_body)
                # Возвращаем ответ
                return response_json["result"]
        except urllib.error.HTTPError as e:
            # Это напечатает точную причину ошибки от самого Телеграма!
            print("Telegram API Error Body:", e.read().decode("utf-8"))
            raise

    # Метод getUpdates запрашивает данные с сервера
    # offset - параметр метода getUpdates, можно посмотреть в доке TG Bot API
    # https://core.telegram.org/bots/api
    ## UPD: Замена в запросе обновления конкретного типа данных, на любой тип данных
    ## Тоже самое делает в main
    def getUpdates(self, **params) -> dict:
        # Используем новую функцию для создания универсальных запросов
        return self.makeRequest("getUpdates", **params)

    # sendMessage принимает сообщения которые отправлены в бота
    # так же принимает аргументами параметры для sendMessage
    ## UPD: Явно указываем что могут быть и другие параметры
    def sendMessage(self, chat_id: int, text: str, **params) -> dict:
        return self.makeRequest("sendMessage", chat_id=chat_id, text=text, **params)

    # getMe способ тестирования токена аутентификации вашего бота. Не требуется никаких параметров
    def getMe(self) -> dict:
        return self.makeRequest("getMe")

    # Удаляет сообщение бота
    def deleteMessage(self, chat_id: int, message_id: int) -> dict:
        return self.makeRequest("deleteMessage", chat_id=chat_id, message_id=message_id)

    def answerCallbackQuery(self, callback_query_id: str, **kwargs) -> dict:
        return self.makeRequest(
            "answerCallbackQuery", callback_query_id=callback_query_id, **kwargs
        )

    def sendInvoice(
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
        return self.makeRequest(
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

    def answerPreCheckoutQuery(
        self, pre_checkout_query_id: str, ok: bool, **kwargs
    ) -> dict:
        return self.makeRequest(
            "answerPreCheckoutQuery",
            pre_checkout_query_id=pre_checkout_query_id,
            ok=ok,
            **kwargs,
        )
