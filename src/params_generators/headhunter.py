from datetime import datetime
from typing import List

from params_generators.utils import merge_dicts, format_date


class ParamsGeneratorHeadhunter:
    """
    Генератор параметров для формирования запросов к API HeadHunter.
    """

    _LOCATIONS_PARAMS = {
        "Москва (офис, удаленно)": {"area": "1"},
        "Санкт-Петербург (офис, удаленно)": {"area": "2"},
        "Удаленно": {"work_format": "REMOTE"},
        "Другие страны": {"area": "1001"},
    }

    _SPETIALITIES_PARAMS = {
        "Тестировщик": {"professional_role": "124"},
        "Дата саентист/аналитик": {"professional_role": "165"},
        "Системный аналитик": {"professional_role": "148"},
        "Бизнес аналитик": {"professional_role": "156"},
        "Продуктовый аналитик": {"professional_role": "164"},
        "DevOps": {"professional_role": "160"},
        "Дизайнер": {"professional_role": "34"},
        "Менеджер продукта": {"professional_role": "73"},
    }

    _GRADES_PARAMS = {
        "Intern-Junior": {"experience": "noExperience"},
        "Junior-Middle": {"experience": "between1And3"},
        "Middle-Senior": {"experience": "between3And6"},
        "Senior+": {"experience": "moreThan6"},
    }

    def _get_params_from_grade(self, grade: str) -> dict:
        """
        Получает параметры фильтрации по уровню опыта.

        Args:
            grade (str): Уровень опыта (например, "Junior-Middle").

        Returns:
            dict: Словарь параметров для фильтрации по опыту.
        """
        return self._GRADES_PARAMS.get(grade, {})

    def _get_params_from_date(self, date: datetime) -> dict:
        """
        Преобразует дату в параметр запроса для фильтрации вакансий по дате публикации.

        Args:
            date (datetime): Дата, с которой нужно фильтровать вакансии.

        Returns:
            dict: Словарь с параметром 'date_from' для запроса.
        """
        return {"date_from": str(format_date(date))}

    def _get_params_from_salary(self, salary: int | float) -> dict:
        """
        Преобразует значение зарплаты в параметр запроса.

        Args:
            salary (int | float): Минимальная зарплата для фильтрации.

        Returns:
            dict: Словарь с параметром 'salary' для запроса.
        """
        return {"salary": salary}

    def _get_params_several(self, characteristics: List[str], params_configurator: dict) -> dict:
        """
        Объединяет параметры для нескольких характеристик (например, локаций или специальностей).

        Args:
            characteristics (List[str]): Список значений характеристик.
            params_configurator (dict): Словарь, где ключ — характеристика, а значение — параметры.

        Returns:
            dict: Объединённый словарь параметров для всех переданных характеристик.
        """
        params = {}
        for characteristic in characteristics:
            if characteristic in params_configurator:
                params = merge_dicts(
                    params, params_configurator[characteristic])
        return params

    def get_params(self, locations: List[str], specialities: List[str], grade: str, salary: float | int, date: datetime) -> dict:
        """
        Формирует итоговый словарь параметров для запроса к API HeadHunter.

        Args:
            locations (List[str]): Список локаций.
            specialities (List[str]): Список специальностей.
            grade (str): Уровень опыта.
            salary (float | int): Минимальная зарплата.
            date (datetime): Дата публикации вакансии.

        Returns:
            dict: Словарь всех параметров для запроса.
        """
        params = {}
        params = merge_dicts(params, self._get_params_several(
            locations, self._LOCATIONS_PARAMS))
        params = merge_dicts(params, self._get_params_several(
            specialities, self._SPETIALITIES_PARAMS))
        params = merge_dicts(params, self._get_params_from_grade(grade))
        params = merge_dicts(params, self._get_params_from_salary(salary))
        params = merge_dicts(params, self._get_params_from_date(date))

        return params
