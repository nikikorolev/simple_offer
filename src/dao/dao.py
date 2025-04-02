from typing import TypeVar, Generic
from sqlalchemy.exc import SQLAlchemyError, MultipleResultsFound, NoResultFound
from sqlalchemy.future import select
from sqlalchemy import delete as sqlalchemy_delete, func, desc
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from dao.database import Base
from dao.models import User, Location, Grade, Salary, Speciality, SentVacanciesHeadhunter


T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    """
    Базовый класс для работы с моделями базы данных.
    """
    model: type[T]

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, filter: dict):
        """
        Ищет одну запись в базе данных по переданному фильтру.
        Возвращает найденную запись или None, если запись не найдена.
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
    async def find_all(cls, session: AsyncSession, filter: dict = {}):
        """
        Ищет все записи в базе данных, соответствующие переданному фильтру.
        Возвращает список найденных записей.
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
    async def add(cls, session: AsyncSession, values: dict):
        """
        Добавляет новую запись в базу данных.
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
    async def get_or_add(cls, session: AsyncSession, values: dict):
        """
        Ищет запись в базе данных по переданному фильтру. Если запись не найдена, создаёт новую.
        """
        obj = await cls.find_one_or_none(session, values)
        if not obj:
            obj = await cls.add(session, values)
        return obj

    @classmethod
    async def delete(cls, session: AsyncSession, filter: dict):
        """
        Удаляет записи из базы данных по переданному фильтру.
        Возвращает количество удалённых записей.
        """
        logger.info(
            f"Удаление записей {cls.model.__name__} по фильтру: {filter}")
        try:
            if not filter:
                logger.error("Нужен хотя бы один фильтр для удаления.")
                raise ValueError("Нужен хотя бы один фильтр для удаления.")
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
    async def count(cls, session: AsyncSession, filter: dict = {}):
        """
        Подсчитывает количество записей в базе данных, соответствующих переданному фильтру.
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
    async def get_last_record(cls, session: AsyncSession, filter: dict = {}):
        """
        Получает последнюю запись в таблице по полю 'created_at'.
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
