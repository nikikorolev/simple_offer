from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List


def get_inline_markup_for_select(
    options: List[str], selected_options: List[str], back_button: bool = True
) -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру для выбора опций (для FSM сценария). 
    """
    buttons: List[List[InlineKeyboardButton]] = [
        [InlineKeyboardButton(
            text=f"⚪ {option}" if option in selected_options else option, callback_data=option)]
        for option in options
    ]

    buttons.append([InlineKeyboardButton(
        text="✅ Завершить выбор", callback_data="finish")])
    buttons.append([InlineKeyboardButton(
        text="🗑 Очистить выбор", callback_data="clear")])

    if back_button:
        buttons.append([InlineKeyboardButton(
            text="⬅️ Назад", callback_data="back")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_inline_markup_send_vacancy(url: str) -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру с кнопкой перехода на вакансию.
    """
    button = InlineKeyboardButton(text="Перейти на вакансию 🔗", url=url)
    return InlineKeyboardMarkup(inline_keyboard=[[button]])
