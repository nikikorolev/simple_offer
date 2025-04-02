from loguru import logger
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.markups import get_inline_markup_for_select
from dao.dao import UserDAO, LocationDAO, SalaryDAO, SpecialityDAO, GradeDAO
from constants import LOCATION_CHOICES, GRADE_CHOICES, SPECIALTY_CHOICES, SALARY_CHOICES

router = Router()


class UserSettings(StatesGroup):
    locations = State()
    specialties = State()
    grades = State()
    salary = State()


@router.message(Command("settings"))
async def cmd_settings(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} вызвал команду настройки.")
    await state.clear()
    await state.update_data(locations=[], specialties=[], grades=[], salary=[])
    await message.answer(
        "📩 *[1/4]* Выберите локацию, в которой хотите работать (можно выбрать несколько):",
        reply_markup=get_inline_markup_for_select(
            LOCATION_CHOICES, [], back_button=False),
        parse_mode="Markdown"
    )
    await state.set_state(UserSettings.locations)
    logger.info(
        f"Состояние установлено на UserSettings.locations для пользователя {user_id}.")


@router.callback_query(UserSettings.locations)
async def location_chosen(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} выбрал локацию: {callback.data}.")
    data = await state.get_data()
    selected_locations = data.get("locations", [])

    if callback.data == "clear":
        selected_locations.clear()
        await state.update_data(locations=selected_locations)
        await callback.message.edit_reply_markup(
            reply_markup=get_inline_markup_for_select(
                LOCATION_CHOICES, selected_locations, back_button=False)
        )
        await callback.answer("🚮 Локации очищены.")
        logger.info(f"Локации очищены для пользователя {user_id}.")
        return

    if callback.data == "finish":
        if not selected_locations:
            await callback.answer("❌ Нужно выбрать хотя бы одну локацию!")
            logger.warning(
                f"Пользователь {user_id} попытался завершить настройку без выбора локации.")
            return
        await callback.message.edit_text(
            "📩 *[2/4]* Теперь выберите специальность:",
            reply_markup=get_inline_markup_for_select(SPECIALTY_CHOICES, []),
            parse_mode="Markdown"
        )
        await state.set_state(UserSettings.specialties)
        logger.info(
            f"Состояние установлено на UserSettings.specialties для пользователя {user_id}.")
        await callback.answer()
        return

    if callback.data in LOCATION_CHOICES:
        if callback.data in selected_locations:
            selected_locations.remove(callback.data)
            logger.info(
                f"Локация {callback.data} удалена из списка пользователя {user_id}.")
        else:
            selected_locations.append(callback.data)
            logger.info(
                f"Локация {callback.data} добавлена в список пользователя {user_id}.")

        await state.update_data(locations=selected_locations)
        await callback.message.edit_reply_markup(
            reply_markup=get_inline_markup_for_select(
                LOCATION_CHOICES, selected_locations, back_button=False)
        )
        await callback.answer()


@router.callback_query(UserSettings.specialties)
async def speciality_chosen(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info(
        f"Пользователь {user_id} выбрал специальность: {callback.data}.")
    data = await state.get_data()
    selected_specialities = data.get("specialties", [])

    if callback.data == "clear":
        selected_specialities.clear()
        await state.update_data(specialties=selected_specialities)
        await callback.message.edit_reply_markup(
            reply_markup=get_inline_markup_for_select(
                SPECIALTY_CHOICES, selected_specialities)
        )
        await callback.answer("🚮 Специальности очищены.")
        logger.info(f"Специальности очищены для пользователя {user_id}.")
        return

    if callback.data == "back":
        await callback.message.edit_text(
            "📩 *[1/4]* Выберите локацию, в которой хотите работать:",
            reply_markup=get_inline_markup_for_select(
                LOCATION_CHOICES, data.get("locations", []), back_button=False),
            parse_mode="Markdown"
        )
        await state.set_state(UserSettings.locations)
        logger.info(
            f"Состояние установлено на UserSettings.locations для пользователя {user_id}.")
        await callback.answer()
        return

    if callback.data == "finish":
        if not selected_specialities:
            await callback.answer("❌ Нужно выбрать хотя бы одну специальность!")
            logger.warning(
                f"Пользователь {user_id} попытался завершить настройку без выбора специальности.")
            return
        await callback.message.edit_text(
            "📩 *[3/4]* Теперь выберите грейд:",
            reply_markup=get_inline_markup_for_select(GRADE_CHOICES, []),
            parse_mode="Markdown"
        )
        await state.set_state(UserSettings.grades)
        logger.info(
            f"Состояние установлено на UserSettings.grades для пользователя {user_id}.")
        await callback.answer()
        return

    if callback.data in SPECIALTY_CHOICES:
        if callback.data in selected_specialities:
            selected_specialities.remove(callback.data)
            logger.info(
                f"Специальность {callback.data} удалена из списка пользователя {user_id}.")
        else:
            selected_specialities.append(callback.data)
            logger.info(
                f"Специальность {callback.data} добавлена в список пользователя {user_id}.")

        await state.update_data(specialties=selected_specialities)
        await callback.message.edit_reply_markup(
            reply_markup=get_inline_markup_for_select(
                SPECIALTY_CHOICES, selected_specialities)
        )
        await callback.answer()


@router.callback_query(UserSettings.grades)
async def grade_chosen(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} выбрал грейд: {callback.data}.")
    data = await state.get_data()
    selected_grades = data.get("grades", [])

    if callback.data == "clear":
        selected_grades.clear()
        await state.update_data(grades=selected_grades)
        await callback.message.edit_reply_markup(
            reply_markup=get_inline_markup_for_select(
                GRADE_CHOICES, selected_grades)
        )
        await callback.answer("🚮 Грейды очищены.")
        logger.info(f"Грейды очищены для пользователя {user_id}.")
        return

    if callback.data == "back":
        await callback.message.edit_text(
            "📩 *[2/4]* Теперь выберите специальность:",
            reply_markup=get_inline_markup_for_select(
                SPECIALTY_CHOICES, data.get("specialties", [])),
            parse_mode="Markdown"
        )
        await state.set_state(UserSettings.specialties)
        logger.info(
            f"Состояние установлено на UserSettings.specialties для пользователя {user_id}.")
        await callback.answer()
        return

    if callback.data == "finish":
        if not selected_grades:
            await callback.answer("❌ Нужно выбрать хотя бы один грейд!")
            logger.warning(
                f"Пользователь {user_id} попытался завершить настройку без выбора грейда.")
            return
        await callback.message.edit_text(
            "📩 *[4/4]* Теперь выберите уровень зарплаты:",
            reply_markup=get_inline_markup_for_select(SALARY_CHOICES, []),
            parse_mode="Markdown"
        )
        await state.set_state(UserSettings.salary)
        logger.info(
            f"Состояние установлено на UserSettings.salary для пользователя {user_id}.")
        await callback.answer()
        return

    if callback.data in GRADE_CHOICES:
        if callback.data in selected_grades:
            selected_grades.remove(callback.data)
            logger.info(
                f"Грейд {callback.data} удален из списка пользователя {user_id}.")
        else:
            selected_grades.append(callback.data)
            logger.info(
                f"Грейд {callback.data} добавлен в список пользователя {user_id}.")

        await state.update_data(grades=selected_grades)
        await callback.message.edit_reply_markup(
            reply_markup=get_inline_markup_for_select(
                GRADE_CHOICES, selected_grades)
        )
        await callback.answer()


@router.callback_query(UserSettings.salary)
async def salary_chosen(callback: CallbackQuery, state: FSMContext, session_with_commit: AsyncSession):
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} выбрал зарплату: {callback.data}.")
    data = await state.get_data()
    selected_salary = data.get("salary", None)

    if callback.data == "clear":
        selected_salary = None
        await state.update_data(salary=selected_salary)
        await callback.message.edit_reply_markup(
            reply_markup=get_inline_markup_for_select(
                SALARY_CHOICES, selected_salary)
        )
        await callback.answer("🚮 Уровень зарплаты очищен.")
        logger.info(f"Зарплата очищена для пользователя {user_id}.")
        return

    if callback.data == "back":
        await callback.message.edit_text(
            "📩 *[3/4]* Теперь выберите грейд:",
            reply_markup=get_inline_markup_for_select(
                GRADE_CHOICES, data.get("grades", [])),
            parse_mode="Markdown"
        )
        await state.set_state(UserSettings.grades)
        logger.info(
            f"Состояние установлено на UserSettings.grades для пользователя {user_id}.")
        await callback.answer()
        return

    if callback.data == "finish":
        if not selected_salary:
            await callback.answer("❌ Нужно выбрать уровень зарплаты!")
            logger.warning(
                f"Пользователь {user_id} попытался завершить настройку без выбора зарплаты.")
            return

        user_settings = await state.get_data()
        user_settings["salary"] = float(selected_salary[:-2]) * 1000

        try:
            user = await UserDAO.get_or_add(session_with_commit, values={
                "telegram_id": user_id})
            logger.info(
                f"Пользователь {user_id} добавлен или найден в базе данных.")

            await LocationDAO.delete(session_with_commit, filter={
                "user_id": user.telegram_id})
            locations = [{"user_id": user.telegram_id, "location": location}
                         for location in user_settings["locations"]]
            for location in locations:
                await LocationDAO.add(session_with_commit, values=location)

            await GradeDAO.delete(session_with_commit, filter={
                "user_id": user.telegram_id})
            grades = [{"user_id": user.telegram_id, "grade": grade}
                      for grade in user_settings["grades"]]
            for grade in grades:
                await GradeDAO.add(session_with_commit, values=grade)

            await SpecialityDAO.delete(session_with_commit, filter={
                "user_id": user.telegram_id})
            specialties = [{"user_id": user.telegram_id, "speciality": speciality}
                           for speciality in user_settings["specialties"]]
            for speciality in specialties:
                await SpecialityDAO.add(session_with_commit, values=speciality)

            await SalaryDAO.delete(session_with_commit, filter={
                "user_id": user.telegram_id})
            await SalaryDAO.add(session_with_commit, values={"user_id": user.telegram_id, "salary": user_settings["salary"]})

            result = (
                f"✅ *Настройки сохранены!*\n\n"
                f"🌍 Локации: {', '.join(user_settings['locations'])}\n"
                f"💼 Специальности: {', '.join(user_settings['specialties'])}\n"
                f"📈 Грейды: {', '.join(user_settings['grades'])}\n"
                f"💰 Уровень зарплаты: более {int(user_settings['salary'])} рублей\n"
            )
            await callback.message.edit_text(result, parse_mode="Markdown")
            logger.info(f"Настройки пользователя {user_id} успешно сохранены.")
        except ValueError as e:
            await callback.answer(f"❌ Ошибка: {e}")
            logger.error(
                f"Ошибка при сохранении настроек пользователя {user_id}: {e}")
        except Exception as e:
            await callback.answer(f"❌ Не удалось добавить пользователя: {str(e)}")
            logger.error(
                f"Не удалось добавить пользователя {user_id}: {str(e)}")

        await state.clear()
        await callback.answer()
        return

    if callback.data in SALARY_CHOICES:
        selected_salary = callback.data

        await state.update_data(salary=selected_salary)
        await callback.message.edit_reply_markup(
            reply_markup=get_inline_markup_for_select(
                SALARY_CHOICES, [selected_salary])
        )
        await callback.answer()
        logger.info(
            f"Зарплата {selected_salary} добавлена в список для пользователя {user_id}.")
