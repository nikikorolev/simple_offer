from aiogram import Bot, Dispatcher
import asyncio
from loguru import logger
from aiogram.fsm.storage.redis import RedisStorage

from settings import TOKEN, REDIS_URL
from handlers import base, user_settings
from handlers.vacancy_sender import VacanciesSender
from database.database import init_db
from database.middleware import DatabaseMiddlewareWithCommit, DatabaseMiddlewareWithoutCommit


async def main():
    await init_db()

    bot = Bot(token=TOKEN)

    redis = RedisStorage.from_url(REDIS_URL)
    dp = Dispatcher(storage=redis)

    dp.update.middleware.register(DatabaseMiddlewareWithoutCommit())
    dp.update.middleware.register(DatabaseMiddlewareWithCommit())

    dp.include_routers(base.router, user_settings.router)

    try:
        logger.info("Bot started!")
        asyncio.create_task(VacanciesSender(bot).start_sending())
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("Bot stopped!")


if __name__ == "__main__":
    asyncio.run(main())
