from datetime import datetime, time
from collections import defaultdict
import asyncio
import json
import os
import aiofiles
import subprocess

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from database.dao import UserDAO, SentVacanciesHeadhunterDAO
from database.database import Session


class AnalyticsParser:
    """
    Класс для аналитики по пользователям и отправленным вакансиям.

    Attributes:
        session (AsyncSession): Асинхронная сессия SQLAlchemy для доступа к БД.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session (AsyncSession): Асинхронная SQLAlchemy-сессия.
        """
        self.session = session

    async def get_count_users(self) -> int:
        """
        Получает общее количество пользователей.

        Returns:
            int: Количество пользователей.
        """
        users = await UserDAO.find_all(self.session, {})
        return len(users)

    async def get_count_new_users_today(self) -> int:
        """
        Получает количество новых пользователей, зарегистрированных сегодня.

        Returns:
            int: Количество новых пользователей за текущие сутки.
        """
        today_start = datetime.combine(datetime.today().date(), time.min)
        users = await UserDAO.find_all(self.session, {})
        new_users = [user for user in users if user.created_at >= today_start]
        return len(new_users)

    async def get_count_messages(self) -> int:
        """
        Получает общее количество отправленных сообщений с вакансиями.

        Returns:
            int: Количество отправленных сообщений.
        """
        messages = await SentVacanciesHeadhunterDAO.find_all(self.session, {})
        return len(messages)

    async def get_count_new_messages_today(self) -> int:
        """
        Получает количество сообщений, отправленных с начала текущего дня.

        Returns:
            int: Количество сообщений за текущие сутки.
        """
        today_start = datetime.combine(datetime.today().date(), time.min)
        messages = await SentVacanciesHeadhunterDAO.find_all(self.session, {})
        new_messages = [
            message for message in messages if message.created_at >= today_start]
        return len(new_messages)

    async def get_count_messages_by_hour_today(self) -> dict:
        """
        Получает количество сообщений, отправленных по часам в течение текущего дня.

        Returns:
            dict: Словарь с двумя списками:
                - 'hours': список часов (int), когда были отправлены сообщения.
                - 'count_messages': количество сообщений в каждый час.
        """
        today_start = datetime.combine(datetime.today().date(), time.min)
        messages = await SentVacanciesHeadhunterDAO.find_all(self.session, {})
        new_messages = [
            message for message in messages if message.created_at >= today_start]
        dates = [
            message.created_at for message in messages if message.created_at >= today_start]

        grouped = defaultdict(list)
        for ts, msg in zip(dates, new_messages):
            grouped[ts.hour].append(msg)

        hours = []
        count_messages = []
        for key, value in grouped.items():
            hours.append(key)
            count_messages.append(len(value))

        return {"hours": hours, "count_messages": count_messages}

    async def get_data(self):
        """
        Собирает статистику активности пользователей и сообщений для аналитики.

        Returns:
            dict: Словарь со следующими ключами:
                - count_users (int): Общее количество пользователей.
                - count_users_today (int): Новые пользователи за сегодня.
                - count_messages (int): Общее количество сообщений.
                - count_messages_today (int): Сообщения за сегодня.
                - count_messages_per_hour (dict): 
                    {
                    'hours' (List[int]): Часы суток (0–23),
                    'count_messages' (List[int]): Количество сообщений по каждому часу
                    }

        Raises:
            Exception: В случае ошибок логирует их через logger и продолжает выполнение.
        """
        try:
            logger.info("Начался сбор данных для аналитики")
            count_users = await self.get_count_users()
            count_users_today = await self.get_count_new_users_today()
            count_messages = await self.get_count_messages()
            count_messages_today = await self.get_count_new_messages_today()
            count_messages_by_hour_today = await self.get_count_messages_by_hour_today()
            logger.info("Закончен сбор данных для аналитики")
        except Exception as e:
            logger.exception(f"Ошибка во время парсинга {e}")

        return {"count_users": count_users,
                "count_users_today": count_users_today,
                "count_messages": count_messages,
                "count_messages_today": count_messages_today,
                "count_messages_per_hour":
                    {
                        "hours": count_messages_by_hour_today['hours'],
                        "count_messages": count_messages_by_hour_today['count_messages']
                    }
                }

    async def save_and_get_data_to_json(self):
        path = "./docs/analytics.json"
        data = await self.get_data()
        logger.info("Началось сохранение данных для аналитики")
        try:
            record = {
                "timestamp": datetime.now().isoformat(),
                "count_users": data["count_users"],
                "count_users_today": data["count_users_today"],
                "count_messages": data["count_messages"],
                "count_messages_today": data["count_messages_today"],
                "count_messages_per_hour": {
                    "hours": data["count_messages_per_hour"]["hours"],
                    "count_messages": data["count_messages_per_hour"]["count_messages"]
                }
            }

            async with aiofiles.open(path, "w") as f:
                await f.write(json.dumps([record], indent=2, ensure_ascii=False))
            logger.info("Данные для аналитики сохранены")
        except Exception as e:
            logger.exception(f"Ошибка во время сохранения данных {e}")

        return record


async def parse_and_save_analytics():
    async with Session() as session:
        scheduler = AsyncIOScheduler()
        parser = AnalyticsParser(session)
        await parser.save_and_get_data_to_json()
        scheduler.add_job(parser.save_and_get_data_to_json,
                          "interval", minutes=5)
        scheduler.start()
        while True:
            await asyncio.sleep(60)
