# Заменяем все вызовы состояний на константы
from enum import Enum


class OrderState(str, Enum):
    WAIT_FOR_PIZZA_NAME = "WAIT_FOR_PIZZA_NAME"
    WAIT_FOR_PIZZA_SIZE = "WAIT_FOR_PIZZA_SIZE"
    WAIT_FOR_DRINKS = "WAIT_FOR_DRINKS"
    WAIT_FOR_ORDER = "WAIT_FOR_ORDER"
    ORDER_CONFIRM = "ORDER_CONFIRM"
    ORDER_CANCEL = "ORDER_CANCEL"
