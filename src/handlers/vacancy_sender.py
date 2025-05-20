from loguru import logger
import asyncio
from typing import List, Dict, Optional, Tuple
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from collectors.headhunter import HeadhunterVacanciesParser
from params_generators.headhunter import ParamsGeneratorHeadhunter
from database.dao import (
    UserDAO, SentVacanciesHeadhunterDAO
)
from database.database import Session
from database.services import UserSettingsServices
from database.models import (
    User, Location, Salary,
    Grade, Speciality
)
from keyboards.markups import get_inline_markup_send_vacancy
from handlers.utils import clean_text_from_html


class VacanciesFinder:
    """Поиск вакансий для пользователя, чтобы отправить их в чат."""

    def __init__(self, session: AsyncSession, telegram_id: str) -> None:
        """
        Args:
            session (AsyncSession): Сессия SQLAlchemy.
            telegram_id (str): Идентификатор пользователя Telegram.
        """
        self.session = session
        self.telegram_id = telegram_id
        if not self.telegram_id:
            raise ValueError("telegram_id не должен быть пустым!")

    async def _get_user_settings(self) -> Tuple[List[Location], List[Speciality], List[Grade], Optional[Salary]]:
        """
        Получение пользовательских настроек по telegram_id.

        Returns:
            Tuple[List[Location], List[Speciality], List[Grade], Optional[Salary]]: 
            Кортеж из списков Location, Speciality, Grade и одного объекта Salary (может быть None).
        """
        return await UserSettingsServices(self.session).get_user_settings_by_telegram_id(self.telegram_id)

    async def _get_last_message_date_headhunter(self) -> Optional[str]:
        """
        Получение даты последней отправленной вакансии.

        Returns:
            Optional[str]: Дата в строковом формате или None, если даты нет.
        """
        return await SentVacanciesHeadhunterDAO.get_last_date_by_telegram_id(
            self.session, self.telegram_id
        )

    async def _get_listed_data_from_user_settings_and_last_date_headhunter(self) -> Tuple[List[str], List[str], List[str], int, Optional[str]]:
        """
        Формирует параметры поиска: локации, специальности, грейды, зарплата, дата.

        Returns:
            Tuple[List[str], List[str], List[str], int, Optional[str]]:
                - Списки локаций, специальностей, грейдов,
                - Зарплата (int),
                - Дата последнего сообщения (str или None).
        """
        locations, specialities, grades, salary = await self._get_user_settings()
        locations = [obj.location for obj in locations]
        grades = [obj.grade for obj in grades]
        specialities = [obj.speciality for obj in specialities]
        salary_value = int(salary.salary) if salary else 0
        date = await self._get_last_message_date_headhunter()
        return locations, specialities, grades, salary_value, date

    async def _generate_params_headhunter(self) -> List[Dict]:
        """
        Генерация параметров поиска для HeadHunter.

        Returns:
            List[Dict]: Список словарей с параметрами для поиска вакансий.
        """
        try:
            logger.info("Формирование параметров для поиска вакансий...")
            locations, specialities, grades, salary, date = await self._get_listed_data_from_user_settings_and_last_date_headhunter()
            headhunter_params = [
                ParamsGeneratorHeadhunter().get_params(
                    locations, specialities, grade, salary, date)
                for grade in grades
            ]
            logger.info(f"Параметров для поиска: {len(headhunter_params)}")
            return headhunter_params
        except Exception as e:
            logger.error(f"Ошибка при формировании параметров: {e}")
            raise

    async def find_vacancies_headhunter(self) -> List[Dict]:
        """
        Поиск вакансий с помощью HeadHunter.

        Returns:
            List[Dict]: Список найденных вакансий.
        """
        headhunter_params = await self._generate_params_headhunter()
        vacancies = []
        for params in headhunter_params:
            parser = HeadhunterVacanciesParser(params=params)
            vacancies_part = await parser.get_all_vacancies()
            if vacancies_part:
                logger.info(
                    f"Найдено {len(vacancies_part)} вакансий по параметрам: {params}")
                vacancies.extend(vacancies_part)
        return vacancies

    async def find_vacancies(self) -> List[Dict]:
        """
        Общий метод для поиска всех доступных вакансий.

        Returns:
            List[Dict]: Список всех найденных вакансий.
        """
        return await self.find_vacancies_headhunter()


class VacanciesSender:
    """Отправка найденных вакансий пользователям Telegram."""

    def __init__(self, bot: Bot, max_concurrent_users: int = 20):
        """
        Args:
            bot (Bot): Экземпляр Telegram-бота.
            max_concurrent_users (int): Максимальное число одновременно обрабатываемых пользователей.
        """
        self.bot = bot
        self.semaphore = asyncio.Semaphore(max_concurrent_users)

    async def is_vacancy_sending(self, session: AsyncSession, vacancy_id: str, telegram_id: int) -> bool:
        """
        Проверка, была ли вакансия уже отправлена пользователю.

        Args:
            session (AsyncSession): Сессия SQLAlchemy.
            vacancy_id (str): ID вакансии.
            telegram_id (int): Telegram ID пользователя.

        Returns:
            bool: True, если уже отправлялась, иначе False.
        """
        try:
            logger.info(f"Проверка вакансии {vacancy_id}")
            filter_ = {"user_id": telegram_id, "vacancy_id": vacancy_id}
            vacancy = await SentVacanciesHeadhunterDAO.get_last_record(session, filter_)
            if vacancy:
                logger.info(f"Вакансия {vacancy_id} уже была отправлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка при проверке вакансии: {e}")
            raise

    @staticmethod
    def generate_message_for_vacancy(vacancy: Dict) -> str:
        """
        Генерация текстового сообщения для вакансии.

        Args:
            vacancy (Dict): Данные вакансии.

        Returns:
            str: Сформированное сообщение.
        """
        if vacancy['salary_from'] and vacancy['salary_to']:
            salary_string = f"{vacancy['salary_from']} - {vacancy['salary_to']} {vacancy['salary_currency']}"
        elif vacancy['salary_from']:
            salary_string = f"{vacancy['salary_from']} {vacancy['salary_currency']}"
        elif vacancy['salary_to']:
            salary_string = f"{vacancy['salary_to']} {vacancy['salary_currency']}"
        else:
            salary_string = "Зарплата не указана"

        return (
            f"*{vacancy['name']}* @ *{vacancy['employer']}*\n\n"
            f"💰 {salary_string}\n"
            f"📍 {vacancy['location']}\n\n"
            f"Требуемые навыки: {clean_text_from_html(vacancy['description'])}\n\n"
            f"Обязанности: {clean_text_from_html(vacancy['responsibility'])}"
        )

    async def vacancy_sending(self, vacancy: Dict, telegram_id: int) -> None:
        """
        Отправка вакансии пользователю через Telegram.

        Args:
            vacancy (Dict): Вакансия.
            telegram_id (int): Telegram ID пользователя.

        Returns:
            None
        """
        try:
            logger.info(
                f"Отправка вакансии {vacancy['id']} пользователю {telegram_id}")
            message = self.generate_message_for_vacancy(vacancy)
            await self.bot.send_message(
                telegram_id,
                message,
                reply_markup=get_inline_markup_send_vacancy(vacancy['link']),
                parse_mode="Markdown"
            )
            logger.info(
                f"Вакансия {vacancy['id']} отправлена пользователю {telegram_id}")
        except Exception as e:
            logger.error(f"Ошибка при отправке вакансии: {e}")
            raise

    async def vacancy_saving(self, session: AsyncSession, vacancy: Dict, telegram_id: int) -> None:
        """
        Сохранение информации о том, что вакансия была отправлена.

        Args:
            session (AsyncSession): Сессия SQLAlchemy.
            vacancy (Dict): Вакансия.
            telegram_id (int): Telegram ID пользователя.

        Returns:
            None
        """
        values = {"user_id": telegram_id, "vacancy_id": str(vacancy['id'])}
        await SentVacanciesHeadhunterDAO.add(session, values)

    async def process_user(self, session: AsyncSession, user: User, timeout: int = 30) -> None:
        """
        Обработка одного пользователя — поиск и отправка вакансий.

        Args:
            session (AsyncSession): Сессия SQLAlchemy.
            user (User): Объект пользователя.
            timeout (int): Максимальное время ожидания.

        Returns:
            None
        """
        telegram_id = user.telegram_id
        async with self.semaphore:
            try:
                logger.info(f"Обработка пользователя {telegram_id}")
                vacancies = await asyncio.wait_for(
                    VacanciesFinder(session, telegram_id).find_vacancies(),
                    timeout=timeout
                )
                for vacancy in vacancies:
                    if not await self.is_vacancy_sending(session, vacancy["id"], telegram_id):
                        await asyncio.wait_for(self.vacancy_sending(vacancy, telegram_id), timeout=10)
                        await self.vacancy_saving(session, vacancy, telegram_id)
                        await asyncio.sleep(0.5)
            except asyncio.TimeoutError:
                logger.warning(
                    f"Timeout при обработке пользователя {telegram_id}")
            except Exception as e:
                logger.error(
                    f"Ошибка при обработке пользователя {telegram_id}: {e}")

    async def start_sending(self, sleep_time: int = 10) -> None:
        """
        Запускает цикл отправки вакансий всем пользователям.

        Args:
            sleep_time (int): Задержка между итерациями (сек).

        Returns:
            None
        """
        while True:
            async with Session() as session:
                try:
                    users = await UserDAO.find_all(session, {})
                    logger.info(
                        f"Начинаем обработку {len(users)} пользователей")
                    tasks = [self.process_user(session, user)
                             for user in users]
                    await asyncio.gather(*tasks)
                    await session.commit()
                except Exception as e:
                    logger.error(
                        f"Глобальная ошибка в процессе отправки вакансий: {e}")
                finally:
                    await session.close()
                    logger.info("Сессия sender закрыта")
            await asyncio.sleep(sleep_time)
