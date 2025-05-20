from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from database.services import UserSettingsServices


router = Router()


@router.message(Command(commands=["start", "help"]))
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} вызвал команду: {message.text}")

    await state.clear()
    command_name = "start" if "start" in message.text else "help"

    if command_name == "start":
        text = (
            f"👋 *Привет, {message.from_user.first_name}!* \n\n"
            "🚀 Давай настроим бота, чтобы он идеально подходил под твои запросы\n"
            "👉 Для начала настроек нажми /settings\n"
        )
        logger.info(
            f"Приветственное сообщение отправлено пользователю {user_id}.")
    if command_name == "help":
        text = (
            "📚 *Доступные команды:*\n\n"
            "👉 /start — начать работу с ботом 🚀\n"
            "👉 /help — открыть список команд 📝\n"
            "👉 /settings — изменить настройки ⚙️\n"
            "👉 /my\_settings — сохраненные настройки ⚙️\n")
        logger.info(
            f"Сообщение с командой помощи отправлено пользователю {user_id}.")

    await message.answer(
        text,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    logger.info(f"Ответ на команду отправлен пользователю {user_id}.")


@router.message(Command(commands=["my_settings"]))
async def cmd_start(message: Message, state: FSMContext, session_without_commit: AsyncSession):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} вызвал команду: {message.text}")

    await state.clear()
    services = UserSettingsServices(
        session_without_commit)
    settings = await services.get_user_settings_by_telegram_id(user_id)
    if settings[3]:
        locations, specialties, grades, salary = services.get_listed_data_from_user_settings(
            *settings)
        text = (
            f"✅ *Твои настройки:*\n\n"
            f"🌍 Локации: {', '.join(locations)}\n"
            f"💼 Специальности: {', '.join(specialties)}\n"
            f"📈 Грейды: {', '.join(grades)}\n"
            f"💰 Уровень зарплаты: более {int(salary)} рублей\n"
        )
    else:
        text = f"❌ Ты еще не сохранял свои настройки! 👉 Жми /settings"

    await message.answer(
        text,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    logger.info(f"Ответ на команду отправлен пользователю {user_id}.")
