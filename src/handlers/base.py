from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from loguru import logger


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
            "👉 /settings — изменить настройки ⚙️\n")
        logger.info(
            f"Сообщение с командой помощи отправлено пользователю {user_id}.")

    await message.answer(
        text,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    logger.info(f"Ответ на команду отправлен пользователю {user_id}.")
