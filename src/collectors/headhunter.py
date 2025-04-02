import aiohttp
from loguru import logger
from typing import List, Dict, Optional


class HeadhunterVacanciesParser:
    """Парсер для headhunter-а"""

    def __init__(self, params: Optional[Dict[str, str]] = None, per_page: int = 20):
        """
        Инициализация парсера вакансий с параметрами для запроса.
        """
        self.base_url = "https://api.hh.ru/vacancies"
        self.params = params or {}
        self.per_page = per_page

    async def get_vacancies(self, session: aiohttp.ClientSession, page: int = 0) -> Optional[Dict]:
        """
        Получение данных о вакансиях для конкретной страницы.
        """
        params = self.params.copy()
        params["page"] = page
        params["per_page"] = self.per_page
        try:
            logger.debug(
                f"Отправка запроса на получение вакансий, страница {page}")
            async with session.get(self.base_url, params=params) as response:
                response.raise_for_status()
                logger.debug(
                    f"Запрос выполнен успешно. Код ответа: {response.status}")
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка при запросе данных на странице {page}: {e}")
            return None

    async def get_pages(self, session: aiohttp.ClientSession) -> int:
        """
        Получение общего числа страниц для всех вакансий.
        """
        vacancies_data = await self.get_vacancies(session, page=0)
        if vacancies_data:
            logger.debug(
                f"Количество страниц с вакансиями: {vacancies_data["pages"]}")
            return vacancies_data["pages"]
        else:
            logger.debug("Не удалось получить данные о страницах.")
            return 0

    def parse_vacancies(self, vacancies_data: Dict) -> List[Dict[str, Optional[str]]]:
        """
        Парсинг данных вакансий из ответа API.
        """
        if not vacancies_data:
            logger.debug("Отсутствуют данные для парсинга.")
            return []

        vacancies = []
        logger.debug(
            f"Парсинг {len(vacancies_data.get("items", []))} вакансий.")
        for vacancy in vacancies_data.get("items", []):
            vac_info = {
                "id": vacancy["id"],
                "name": vacancy["name"],
                "salary_from": vacancy["salary"]["from"] if vacancy["salary"] else None,
                "salary_to": vacancy["salary"]["to"] if vacancy["salary"] else None,
                "salary_currency": vacancy["salary"]["currency"] if vacancy["salary"] else None,
                "location": vacancy["area"]["name"] if vacancy.get("area") else None,
                "employer": vacancy["employer"]["name"] if vacancy.get("employer") else None,
                "link": vacancy["alternate_url"],
                "description": vacancy["snippet"]["requirement"] if vacancy.get("snippet") else "",
                "responsibility": vacancy["snippet"]["responsibility"] if vacancy.get("snippet") else "",
            }
            vacancies.append(vac_info)
        logger.debug(f"Парсинг завершен. Найдено {len(vacancies)} вакансий.")
        return vacancies

    async def get_all_vacancies(self) -> List[Dict[str, Optional[str]]]:
        """
        Получение всех вакансий, проходя по всем страницам.
        """
        async with aiohttp.ClientSession() as session:
            pages = await self.get_pages(session)
            all_vacancies = []
            logger.debug(
                f"Начало получения всех вакансий. Всего страниц: {pages}")

            for page in range(pages):
                logger.debug(f"Получение вакансий с страницы {page}")
                vacancies_data = await self.get_vacancies(session, page)
                if vacancies_data is None or not vacancies_data.get("items"):
                    logger.debug(
                        f"Нет вакансий на странице {page}, завершение парсинга.")
                    break

                parsed_vacancies = self.parse_vacancies(vacancies_data)
                all_vacancies.extend(parsed_vacancies)

                if len(vacancies_data["items"]) < self.per_page:
                    logger.debug(
                        f"Количество вакансий на странице {page} меньше {self.per_page}, завершение парсинга.")
                    break

            logger.debug(
                f"Общее количество полученных вакансий: {len(all_vacancies)}")
            return all_vacancies
