# Мини утилита для проверки JSON
import json


def inspect(update):
    print(json.dumps(update, indent=2, ensure_ascii=False))