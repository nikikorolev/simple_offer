import aiohttp
from loguru import logger
from typing import List, Dict, Optional, Union


class HeadhunterVacanciesParser:
    """
    Парсер для получения вакансий с API HeadHunter.

    Args:
        params (Optional[Dict[str, str]]): Параметры запроса к API.
        per_page (int): Количество вакансий на странице (пагинация).
    """

    def __init__(self, params: Optional[Dict[str, str]] = None, per_page: int = 20) -> None:
        self.base_url: str = "https://api.hh.ru/vacancies"
        self.params: Dict[str, str] = params or {}
        self.per_page: int = per_page

    async def get_vacancies(self, session: aiohttp.ClientSession, page: int = 0) -> Optional[Dict]:
        """
        Получить данные о вакансиях с конкретной страницы.

        Args:
            session (aiohttp.ClientSession): Асинхронная сессия для HTTP запросов.
            page (int): Номер страницы для пагинации.

        Returns:
            Optional[Dict]: Словарь с ответом API или None при ошибке.
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
        Получить общее количество страниц с вакансиями.

        Args:
            session (aiohttp.ClientSession): Асинхронная сессия.

        Returns:
            int: Количество страниц.
        """
        vacancies_data = await self.get_vacancies(session, page=0)
        if vacancies_data and "pages" in vacancies_data:
            logger.debug(
                f"Количество страниц с вакансиями: {vacancies_data['pages']}")
            return vacancies_data["pages"]
        logger.debug("Не удалось получить данные о страницах.")
        return 0

    def parse_vacancies(self, vacancies_data: Dict) -> List[Dict[str, Optional[Union[str, int]]]]:
        """
        Распарсить вакансии из ответа API.

        Args:
            vacancies_data (Dict): Данные ответа API.

        Returns:
            List[Dict[str, Optional[Union[str, int]]]]: Список вакансий с нужными полями.
        """
        if not vacancies_data:
            logger.debug("Отсутствуют данные для парсинга.")
            return []

        items = vacancies_data.get("items", [])
        logger.debug(f"Парсинг {len(items)} вакансий.")
        vacancies: List[Dict[str, Optional[Union[str, int]]]] = []

        for vacancy in items:
            salary = vacancy.get("salary")
            snippet = vacancy.get("snippet", {})
            vac_info = {
                "id": vacancy.get("id"),
                "name": vacancy.get("name"),
                "salary_from": salary.get("from") if salary else None,
                "salary_to": salary.get("to") if salary else None,
                "salary_currency": salary.get("currency") if salary else None,
                "location": vacancy.get("area", {}).get("name") if vacancy.get("area") else None,
                "employer": vacancy.get("employer", {}).get("name") if vacancy.get("employer") else None,
                "link": vacancy.get("alternate_url"),
                "description": snippet.get("requirement", ""),
                "responsibility": snippet.get("responsibility", ""),
            }
            vacancies.append(vac_info)

        logger.debug(f"Парсинг завершен. Найдено {len(vacancies)} вакансий.")
        return vacancies

    async def get_all_vacancies(self) -> List[Dict[str, Optional[Union[str, int]]]]:
        """
        Получить все вакансии, обходя все страницы.

        Returns:
            List[Dict[str, Optional[Union[str, int]]]]: Полный список вакансий.
        """
        async with aiohttp.ClientSession() as session:
            pages = await self.get_pages(session)
            all_vacancies: List[Dict[str, Optional[Union[str, int]]]] = []
            logger.debug(
                f"Начало получения всех вакансий. Всего страниц: {pages}")

            for page in range(pages):
                logger.debug(f"Получение вакансий с страницы {page}")
                vacancies_data = await self.get_vacancies(session, page)
                if not vacancies_data or not vacancies_data.get("items"):
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
