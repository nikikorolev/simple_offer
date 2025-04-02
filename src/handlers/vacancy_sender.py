from loguru import logger
import asyncio
from typing import List, Dict, Optional

from collectors.headhunter import HeadhunterVacanciesParser
from params_generators.headhunter import ParamsGeneratorHeadhunter
from dao.dao import UserDAO, LocationDAO, SalaryDAO, SpecialityDAO, GradeDAO, SentVacanciesHeadhunterDAO
from dao.database import Session
from keyboards.markups import get_inline_markup_send_vacancy
from handlers.utils import clean_text_from_html


class Sender:
    def __init__(self, bot):
        """
        Инициализация класса Sender для отправки вакансий пользователям.
        """
        self.bot = bot

    async def get_settings_objects_by_telegram_id(self, session, telegram_id: int) -> tuple:
        """
        Получение настроек пользователя для дальнейшей фильтрации вакансий.
        """
        try:
            logger.info(
                f"Получение настроек для пользователя с ID: {telegram_id}")
            filter = {"user_id": telegram_id}
            locations = await LocationDAO.find_all(session, filter)
            grades = await GradeDAO.find_all(session, filter)
            specialities = await SpecialityDAO.find_all(session, filter)
            salary = await SalaryDAO.find_one_or_none(session, filter)
            logger.info(
                f"Настройки успешно получены для пользователя с ID: {telegram_id}")
            return locations, grades, specialities, salary
        except Exception as e:
            logger.error(
                f"Ошибка при получении настроек для пользователя с ID {telegram_id}: {e}")
            raise

    async def get_last_date(self, session, salary, telegram_id: int) -> str:
        """
        Получение даты последней отправленной вакансии для пользователя.
        """
        try:
            logger.info(
                f"Получение последней записи отправленных вакансий для пользователя с ID: {telegram_id}")
            filter = {"user_id": telegram_id}
            last_record = await SentVacanciesHeadhunterDAO.get_last_record(session, filter)
            if not last_record:
                date = salary.updated_at
                logger.info(
                    f"Нет предыдущей записи для пользователя {telegram_id}, устанавливаем дату обновления: {date}")
            else:
                date = last_record.updated_at
                logger.info(
                    f"Используем дату последней вакансии для пользователя {telegram_id}: {date}")
            return date
        except Exception as e:
            logger.error(
                f"Ошибка при получении последней записи отправленных вакансий для пользователя с ID {telegram_id}: {e}")
            raise

    def get_params_to_response(self, locations: List[object], specialities: List[object], grades: List[object], salary: object, date: str) -> List[dict]:
        """
        Формирование параметров для поиска вакансий на основе настроек пользователя.
        """
        try:
            logger.info("Формирование параметров для поиска вакансий...")
            locations = [object.location for object in locations]
            grades = [object.grade for object in grades]
            specialities = [object.speciality for object in specialities]
            salary = int(salary.salary)
            params_list = []
            for grade in grades:
                params = ParamsGeneratorHeadhunter().get_params(
                    locations, specialities, grade, salary, date)
                params_list.append(params)
            logger.info(
                f"Параметры для поиска вакансий сформированы: {len(params_list)} параметров")
            return params_list
        except Exception as e:
            logger.error(
                f"Ошибка при формировании параметров для поиска вакансий: {e}")
            raise

    async def vacancies_parsing(self, session, telegram_id: int) -> List[Dict[str, Optional[str]]]:
        """
        Парсинг вакансий для пользователя по его настройкам.
        """
        locations, grades, specialities, salary = await self.get_settings_objects_by_telegram_id(session, telegram_id)
        date = await self.get_last_date(session, salary, telegram_id)
        params_list = self.get_params_to_response(
            locations, specialities, grades, salary, date)

        vacancies = []
        for params in params_list:
            parser = HeadhunterVacanciesParser(params=params)
            vacancies_part = await parser.get_all_vacancies()
            if vacancies_part:
                logger.info(
                    f"Найдено {len(vacancies_part)} вакансий по параметрам: {params}")
                vacancies.extend(vacancies_part)
        return vacancies

    async def is_vacancy_sending(self, session, vacancy_id: str, telegram_id: int) -> bool:
        """
        Проверка, была ли уже отправлена вакансия пользователю.
        """
        try:
            logger.info(f"Проверка вакансии {vacancy_id}")
            filter = {"user_id": telegram_id, "vacancy_id": vacancy_id}
            vacancy = await SentVacanciesHeadhunterDAO().get_last_record(session, filter)
            if vacancy:
                logger.info(f"Вакансия {vacancy_id} уже была отправлена")
                return True
            logger.info(f"Вакансия {vacancy_id} еще не отправлена")
            return False
        except Exception as e:
            logger.error(f"Ошибка в процессе проверки вакансии: {e}")
            raise

    async def vacancy_sending(self, vacancy: dict, telegram_id: int):
        """
        Отправка вакансии пользователю через Telegram.
        """
        try:
            logger.info(
                f"Отправка {vacancy['id']} вакансии пользователю {telegram_id}")
            if vacancy['salary_from'] and vacancy['salary_to']:
                salary_string = f"{vacancy['salary_from']} - {vacancy['salary_to']} {vacancy['salary_currency']}"
            elif vacancy['salary_from']:
                salary_string = f"{vacancy['salary_from']} {vacancy['salary_currency']}"
            elif vacancy['salary_to']:
                salary_string = f"{vacancy['salary_to']} {vacancy['salary_currency']}"
            else:
                salary_string = "Зарплата не указана"

            message = (f"*{vacancy['name']}* @ *{vacancy['employer']}*\n\n"
                       f"💰 {salary_string}\n"
                       f"📍 {vacancy['location']}\n\n"
                       f"Требуемые навыки: {clean_text_from_html(vacancy['description'])}\n\n"
                       f"Обязанности: {clean_text_from_html(vacancy['responsibility'])}")
            await self.bot.send_message(telegram_id, message,
                                        reply_markup=get_inline_markup_send_vacancy(
                                            vacancy['link']),
                                        parse_mode="Markdown")
            logger.info(f"Вакансия отправлена пользователю {telegram_id}")
        except Exception as e:
            logger.error(f"Ошибка в процессе отправки вакансии: {e}")
            raise

    async def vacancy_saving(self, session, vacancy: dict, telegram_id: int):
        """
        Сохранение информации о вакансии, которая была отправлена пользователю.
        """
        values = {"user_id": telegram_id, "vacancy_id": vacancy['id']}
        await SentVacanciesHeadhunterDAO.add(session, values)

    async def start_sending(self, sleep_time: int = 10):
        """
        Основной метод для периодической отправки вакансий пользователям.
        """
        while True:
            async with Session() as session:
                try:
                    users = await UserDAO.find_all(session, {})
                    for user in users:
                        telegram_id = user.telegram_id
                        vacancies = await self.vacancies_parsing(session, telegram_id)
                        if vacancies:
                            for vacancy in vacancies:
                                is_sending = await self.is_vacancy_sending(session, vacancy["id"], telegram_id)
                                if not is_sending:
                                    await self.vacancy_sending(vacancy, telegram_id)
                                    await self.vacancy_saving(session, vacancy, telegram_id)
                    await session.commit()
                except Exception as e:
                    logger.error(f"Ошибка в процессе отправки вакансий: {e}")
                finally:
                    await session.close()
                    logger.info("Сессия для sender закрыта.")
            await asyncio.sleep(sleep_time)
