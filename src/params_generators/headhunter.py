from typing import List
from datetime import datetime

from .utils import merge_dicts, format_date


class ParamsGeneratorHeadhunter:
    """
    Генератор параметров для запросов к HeadHunter API.

    Использует предопределенные параметры для фильтрации вакансий 
    по локации, специальности, уровню опыта, зарплате и дате публикации.
    """

    __LOCATIONS_PARAMS = {
        "Москва (офис, удаленно)": {"area": "1"},
        "Санкт-Петербург (офис, удаленно)": {"area": "2"},
        "Удаленно": {"work_format": "REMOTE"},
        "Другие страны": {"area": "1001"},
    }

    __SPETIALITIES_PARAMS = {
        "Тестировщик": {"professional_role": "124", "text": "QA python java"},
        "Data Scientist/Analyst": {"professional_role": "165"},
        "System Analyst": {"professional_role": "148"},
        "BI Analyst": {"professional_role": "156"},
        "Product Analyst": {"professional_role": "164"},
        "DevOps": {"professional_role": "160"},
        "Designer": {"professional_role": "34"},
        "Product Manager": {"professional_role": "73"},
    }

    __GRADES_PARAMS = {
        "Intern-Junior": {"experience": "noExperience"},
        "Junior-Middle": {"experience": "between1And3"},
        "Middle-Senior": {"experience": "between3And6"},
        "Senior+": {"experience": "moreThan6"},
    }

    def __get_params_from_grade(self, grade: str) -> dict:
        """
        Получает параметры для запроса по уровню опыта.
        """
        return self.__GRADES_PARAMS.get(grade, {})

    def __get_params_from_date(self, date: datetime) -> dict:
        """
        Преобразует дату в параметр запроса.
        """
        return {"date_from": str(format_date(date))}

    def __get_params_from_salary(self, salary: int | float) -> dict:
        """
        Преобразует зарплату в параметр запроса.
        """
        return {"salary": salary}

    def __get_params_several(self, characteristics: List[str], params_configurator: dict) -> dict:
        """
        Объединяет параметры для списка характеристик. 
        characteristics: Список значений (например, локации или специальности).
        params_configurator: Словарь с параметрами для этих характеристик.
        """
        params = {}
        for characteristic in characteristics:
            if characteristic in params_configurator:
                params = merge_dicts(
                    params, params_configurator[characteristic])
        return params

    def get_params(self, locations: List[str], specialities: List[str], grade: str, salary: float | int, date: datetime) -> dict:
        """
        Формирует окончательный набор параметров для запроса.
        """
        params = {}
        params = merge_dicts(params, self.__get_params_several(
            locations, self.__LOCATIONS_PARAMS))
        params = merge_dicts(params, self.__get_params_several(
            specialities, self.__SPETIALITIES_PARAMS))
        params = merge_dicts(params, self.__get_params_from_grade(grade))
        params = merge_dicts(params, self.__get_params_from_salary(salary))
        params = merge_dicts(params, self.__get_params_from_date(date))

        return params
