from datetime import datetime
from sqlalchemy import func, TIMESTAMP, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, async_sessionmaker, create_async_engine

from settings import DATABASE_URL


engine = create_async_engine(
    DATABASE_URL
)

Session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession
)


class Base(AsyncAttrs, DeclarativeBase):
    """
    Абстрактная базовая модель для всех таблиц базы данных.
    Определяет общие поля ID, даты создания и обновления записей.
    """
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )


async def init_db():
    """
    Инициализация базы данных: создание всех таблиц на основе моделей.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
