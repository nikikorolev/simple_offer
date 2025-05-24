import asyncio
from loguru import logger

from analytics.push import push_analytics

SLEEP_TIME = 3600 * 3  # Интервал между запусками задачи в секундах (3 часа)


async def safe_push_analytics():
    """
    Асинхронно вызывает функцию push_analytics с обработкой исключений.

    Returns:
        None

    Raises:
        Исключения не пробрасываются наружу, а логируются внутри функции.
    """
    try:
        await push_analytics()
    except Exception as e:
        logger.error(f"Ошибка в push_analytics: {e}")


async def parse_and_push_analytics():
    """
    Асинхронно запускает бесконечный цикл, который периодически вызывает safe_push_analytics.

    Между вызовами делает паузу длительностью SLEEP_TIME секунд.

    Returns:
        None
    """
    while True:
        await safe_push_analytics()
        await asyncio.sleep(SLEEP_TIME)
