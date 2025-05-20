from typing import Callable, Dict, Any, Awaitable
from abc import ABC, abstractmethod
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from database.database import Session


class BaseDatabaseMiddleware(BaseMiddleware, ABC):
    """
    Базовый middleware для работы с базой данных.
    Открывает сессию перед обработкой события и закрывает её после.
    Дочерние классы должны определить способ установки сессии в данные.
    """

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """
        Вызывается при обработке события.
        Открывает сессию, передаёт её в обработчик и закрывает после завершения.
        """
        async with Session() as session:
            self.set_session(data, session)
            try:
                result = await handler(event, data)
                await self.after_handler(session)
                return result
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    @abstractmethod
    def set_session(self, data: Dict[str, Any], session) -> None:
        """
        Метод для установки сессии в данные.
        """
        pass

    async def after_handler(self, session) -> None:
        """
        Метод для выполнения действий после обработки события.
        """
        pass


class DatabaseMiddlewareWithoutCommit(BaseDatabaseMiddleware):
    """
    Middleware для работы с базой данных без коммита изменений.
    """

    def set_session(self, data: Dict[str, Any], session) -> None:
        """
        Устанавливает сессию без коммита в данные.
        """
        data['session_without_commit'] = session


class DatabaseMiddlewareWithCommit(BaseDatabaseMiddleware):
    """
    Middleware для работы с базой данных с автоматическим коммитом после обработки.
    Используется, если требуется фиксировать изменения в базе данных.
    """

    def set_session(self, data: Dict[str, Any], session) -> None:
        """
        Устанавливает сессию с коммитом в данные.
        """
        data['session_with_commit'] = session

    async def after_handler(self, session) -> None:
        """
        Фиксирует изменения в базе данных после успешного завершения обработки события.
        """
        await session.commit()
