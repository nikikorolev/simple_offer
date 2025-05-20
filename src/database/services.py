from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.models import (
    Location, Salary,
    Grade, Speciality
)
from database.dao import (
    LocationDAO, SalaryDAO,
    GradeDAO, SpecialityDAO
)


class UserSettingsServices:
    """Класс для получения пользовательских настроек из базы данных."""

    def __init__(self, session: AsyncSession):
        """
        Args:
            session (AsyncSession): Асинхронная сессия базы данных.
        """
        self.session = session

    async def get_user_settings_by_telegram_id(
        self, telegram_id: str
    ) -> tuple[List[Location], List[Speciality], List[Grade], List[Salary]]:
        """
        Получение настроек пользователя по telegram_id.

        Args:
            telegram_id (str): Идентификатор пользователя Telegram.

        Returns:
            tuple: Кортеж из списков Location, Speciality, Grade и одного объекта Salary.
        """
        try:
            logger.info(
                f"Получение настроек для пользователя с ID: {telegram_id}")
            filter_params = {"user_id": telegram_id}

            locations = await LocationDAO.find_all(self.session, filter_params)
            grades = await GradeDAO.find_all(self.session, filter_params)
            specialities = await SpecialityDAO.find_all(self.session, filter_params)
            salary = await SalaryDAO.find_one_or_none(self.session, filter_params)

            logger.info(
                f"Настройки успешно получены для пользователя с ID: {telegram_id}")
            return locations, specialities, grades, salary
        except Exception as e:
            logger.error(
                f"Ошибка при получении настроек для пользователя с ID {telegram_id}: {e}")
            raise

    def get_listed_data_from_user_settings(self, locations: List[Location], specialities:  List[Speciality], grades: List[Grade], salary: List[Salary]):
        """

        Получение настроек в виде списка с текстовой информацией.

        Args:
            locations (List[Location]): объекты локаций
            specialities (List[Speciality]): объекты специальностей
            grades (List[Grade]): объекты грейдов
            salary (List[Salary]): зарплата
        """
        locations = [obj.location for obj in locations]
        grades = [obj.grade for obj in grades]
        specialities = [obj.speciality for obj in specialities]
        salary_value = int(salary.salary)
        return locations, specialities, grades, salary_value
