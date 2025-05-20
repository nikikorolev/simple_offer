from typing import TypeVar, Generic, Optional, List
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import delete as sqlalchemy_delete, func, desc
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import Base
from database.models import User, Location, Grade, Salary, Speciality, SentVacanciesHeadhunter


T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    """
    Базовый класс для работы с моделями базы данных.

    Атрибуты:
        model (type[T]): SQLAlchemy-модель, с которой работает DAO.
    """
    model: type[T]

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, filter: dict) -> Optional[T]:
        """
        Ищет одну запись в базе данных по переданному фильтру.
        Возвращает найденную запись или None, если запись не найдена.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            filter (dict): Фильтр для запроса (ключи — имена полей модели).

        Returns:
            Optional[T]: Найденный объект модели или None.
        """
        logger.info(
            f"Поиск одной записи {cls.model.__name__} по фильтрам: {filter}")
        try:
            query = select(cls.model).filter_by(**filter)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            if record:
                logger.info(f"Запись найдена по фильтрам: {filter}")
            else:
                logger.info(f"Запись не найдена по фильтрам: {filter}")
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи по фильтрам {filter}: {e}")
            raise e

    @classmethod
    async def find_all(cls, session: AsyncSession, filter: dict = {}) -> List[T]:
        """
        Ищет все записи в базе данных, соответствующие переданному фильтру.
        Возвращает список найденных записей.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            filter (dict, optional): Фильтр для запроса. По умолчанию пустой.

        Returns:
            List[T]: Список найденных объектов модели.
        """
        logger.info(
            f"Поиск всех записей {cls.model.__name__} по фильтрам: {filter}")
        try:
            query = select(cls.model).filter_by(**filter)
            result = await session.execute(query)
            records = result.scalars().all()
            logger.info(f"Найдено {len(records)} записей.")
            return records
        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при поиске всех записей по фильтрам {filter}: {e}")
            raise e

    @classmethod
    async def add(cls, session: AsyncSession, values: dict) -> T:
        """
        Добавляет новую запись в базу данных.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            values (dict): Словарь с полями и значениями для новой записи.

        Returns:
            T: Созданный объект модели.
        """
        logger.info(
            f"Добавление записи {cls.model.__name__} с параметрами: {values}")
        try:
            new_instance = cls.model(**values)
            session.add(new_instance)
            await session.flush()
            logger.info(f"Запись {cls.model.__name__} успешно добавлена.")
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при добавлении записи: {e}")
            raise e
        return new_instance

    @classmethod
    async def get_or_add(cls, session: AsyncSession, values: dict) -> T:
        """
        Ищет запись в базе данных по переданному фильтру. Если запись не найдена, создаёт новую.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            values (dict): Фильтр и данные для поиска/создания записи.

        Returns:
            T: Найденный или созданный объект модели.
        """
        obj = await cls.find_one_or_none(session, values)
        if not obj:
            obj = await cls.add(session, values)
        return obj

    @classmethod
    async def delete(cls, session: AsyncSession, filter: dict) -> int:
        """
        Удаляет записи из базы данных по переданному фильтру.
        Возвращает количество удалённых записей.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            filter (dict): Фильтр для удаления записей.

        Raises:
            ValueError: Если фильтр пустой.

        Returns:
            int: Количество удалённых записей.
        """
        logger.info(
            f"Удаление записей {cls.model.__name__} по фильтру: {filter}")
        if not filter:
            logger.error("Нужен хотя бы один фильтр для удаления.")
            raise ValueError("Нужен хотя бы один фильтр для удаления.")
        try:
            query = sqlalchemy_delete(cls.model).filter_by(**filter)
            result = await session.execute(query)
            await session.flush()
            logger.info(f"Удалено {result.rowcount} записей.")
            return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при удалении записей: {e}")
            raise e

    @classmethod
    async def count(cls, session: AsyncSession, filter: dict = {}) -> int:
        """
        Подсчитывает количество записей в базе данных, соответствующих переданному фильтру.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            filter (dict, optional): Фильтр для подсчёта. По умолчанию пустой.

        Returns:
            int: Количество найденных записей.
        """
        logger.info(
            f"Подсчет количества записей {cls.model.__name__} по фильтру: {filter}")
        try:
            query = select(func.count(cls.model.id)).filter_by(**filter)
            result = await session.execute(query)
            count = result.scalar()
            logger.info(f"Найдено {count} записей.")
            return count
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при подсчете записей: {e}")
            raise e

    @classmethod
    async def get_last_record(cls, session: AsyncSession, filter: dict = {}) -> Optional[T]:
        """
        Получает последнюю запись в таблице по полю 'created_at'.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            filter (dict, optional): Фильтр для поиска записи. По умолчанию пустой.

        Returns:
            Optional[T]: Последняя запись или None.
        """
        logger.info(f"Поиск последней записи {cls.model.__name__}")
        try:
            query = select(cls.model).filter_by(
                **filter).order_by(desc(cls.model.created_at))
            result = await session.execute(query)
            record = result.scalars().first()
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске последнего сообщения: {e}")
            raise e


class UserDAO(BaseDAO[User]):
    model = User


class LocationDAO(BaseDAO[Location]):
    model = Location


class GradeDAO(BaseDAO[Grade]):
    model = Grade


class SalaryDAO(BaseDAO[Salary]):
    model = Salary


class SpecialityDAO(BaseDAO[Speciality]):
    model = Speciality


class SentVacanciesHeadhunterDAO(BaseDAO[SentVacanciesHeadhunter]):
    model = SentVacanciesHeadhunter

    @classmethod
    async def get_last_date_by_telegram_id(cls, session: AsyncSession, telegram_id: str) -> Optional[str]:
        """
        Получение даты последней отправленной вакансии для пользователя.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            telegram_id (str): Telegram ID пользователя.

        Raises:
            ValueError: Если пользователь с таким Telegram ID не найден.

        Returns:
            Optional[str]: Дата последнего обновления вакансии или пользователя.
        """
        try:
            logger.info(
                f"Получение последней записи отправленных вакансий для пользователя с ID: {telegram_id}")
            user = await UserDAO.find_one_or_none(session, filter={"telegram_id": telegram_id})
            if not user:
                raise ValueError(f"Пользователей с таким {telegram_id} нет!")
            filter_ = {"user_id": telegram_id}
            last_record = await cls.get_last_record(session, filter_)
            date = last_record.updated_at if last_record else user.updated_at
            logger.info(
                f"Используем дату последней вакансии для пользователя {telegram_id}: {date}")
            return date
        except Exception as e:
            logger.error(
                f"Ошибка при получении последней записи отправленных вакансий для пользователя с ID {telegram_id}: {e}")
            raise
