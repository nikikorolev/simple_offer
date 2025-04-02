from collections import defaultdict
from datetime import datetime, timezone, timedelta


def merge_dicts(*dicts):
    """
    Объединяет несколько словарей в один. Если у ключа значение является списком, 
    то элементы списков объединяются. Если значение одиночное, оно добавляется в список.
    """
    target = defaultdict(
        list)
    for d in dicts:
        for key, value in d.items():
            if isinstance(value, list):
                target[key].extend(value)
            else:
                target[key].append(value)

    for key, value in target.items():
        if len(value) == 1:
            target[key] = value[0]

    return dict(target)


def format_date(date: datetime) -> str:
    """
    Форматирует дату в ISO-формат, устанавливая часовой пояс UTC+3.
    """
    return date.replace(tzinfo=timezone(timedelta(hours=3))).isoformat()
