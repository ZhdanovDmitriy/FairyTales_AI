from aiogram.types import CallbackQuery
from keyboards import start_keyboard, settings_keyboard, back_keyboard, sex_keyboard, genre_keyboard
from dbtools import get_user_field, update_user_field
from config import START_MESSAGE, dp, bot

@dp.callback_query(lambda query: query.data == "tale")
async def process_tale(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Выбери, в каком жанре ты бы хотел сказку:", reply_markup=genre_keyboard)
    await update_user_field(callback.from_user.id, 'menu', 21)

@dp.callback_query(lambda query: query.data == "small_tale")
async def process_tale(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Кто будет главным героем сказки?", reply_markup=back_keyboard)
    await update_user_field(callback.from_user.id, 'menu', 311)

@dp.callback_query(lambda query: query.data == "medium_tale")
async def process_tale(callback: CallbackQuery):
    await callback.answer("Данный жанр пока в разработке")

@dp.callback_query(lambda query: query.data == "large_tale")
async def process_tale(callback: CallbackQuery):
    await callback.answer("Данный жанр пока в разработке")

@dp.callback_query(lambda query: query.data == "settings")
async def process_settings(callback: CallbackQuery):
    await callback.message.delete()
    try:
        name = await get_user_field(callback.from_user.id, "name")
        sex = await get_user_field(callback.from_user.id, "sex")
        age = await get_user_field(callback.from_user.id, "age") or "не указано"
        hobby = await get_user_field(callback.from_user.id, "hobby") or "не указано"

        await callback.message.answer(
            f"Имя: {name}\nПол: {sex}\nВозраст: {age}\nХобби: {hobby}\n\nВыберите, что хотите изменить.",
            reply_markup=settings_keyboard
        )
        await update_user_field(callback.from_user.id, 'menu', 22)

    except Exception as e:
        await callback.answer(f"Ошибка при получении данных: {e}")


@dp.callback_query(lambda query: query.data == "back")
async def process_back(callback: CallbackQuery):
    await callback.message.delete()
    if(await get_user_field(callback.from_user.id, "menu") in {314, 321, 22, 21, 311}):
        await callback.message.answer(START_MESSAGE, reply_markup=start_keyboard)
        await update_user_field(callback.from_user.id, 'menu', 321)
    if(await get_user_field(callback.from_user.id, "menu") in {322, 323, 324, 325}):
        try:
            name = await get_user_field(callback.from_user.id, "name")
            sex = await get_user_field(callback.from_user.id, "sex")
            age = await get_user_field(callback.from_user.id, "age") or "не указано"
            hobby = await get_user_field(callback.from_user.id, "hobby") or "не указано"
            await callback.message.answer(f"Имя: {name}\nПол: {sex}\nВозраст: {age}\nХобби: {hobby}\n\nВыберите, что хотите изменить.", reply_markup=settings_keyboard)
            await update_user_field(callback.from_user.id, 'menu', 22)
        except Exception as e:
            await callback.answer(f"Ошибка при получении данных: {e}")
        await update_user_field(callback.from_user.id, 'menu', 22)

@dp.callback_query(lambda query: query.data == "age")
async def process_settings(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Введите ваш возраст:", reply_markup=back_keyboard)
    await update_user_field(callback.from_user.id, 'menu', 323)

@dp.callback_query(lambda query: query.data == "hobby")
async def process_settings(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Напишите кратко, чем ты любишь заниматься:", reply_markup=back_keyboard)
    await update_user_field(callback.from_user.id, 'menu', 324)

@dp.callback_query(lambda query: query.data == "name")
async def process_settings(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Давай знакомиться, как тебя зовут?", reply_markup=back_keyboard)
    await update_user_field(callback.from_user.id, 'menu', 325)

@dp.callback_query(lambda query: query.data == "sex")
async def process_settings(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Выбери свой пол:", reply_markup=sex_keyboard)
    await update_user_field(callback.from_user.id, 'menu', 22)

@dp.callback_query(lambda query: query.data == "man")
async def process_settings(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.delete()
    await update_user_field(user_id, 'sex', "Мужской")
    try:
        name = await get_user_field(callback.from_user.id, "name")
        sex = await get_user_field(callback.from_user.id, "sex")
        age = await get_user_field(callback.from_user.id, "age") or "не указано"
        hobby = await get_user_field(callback.from_user.id, "hobby") or "не указано"
        await callback.message.answer(f"Имя: {name}\nПол: {sex}\nВозраст: {age}\nХобби: {hobby}\n\nВыберите, что хотите изменить.", reply_markup=settings_keyboard)
        await update_user_field(callback.from_user.id, 'menu', 22)
    except Exception as e:
        await callback.answer(f"Ошибка при получении данных: {e}")
    await update_user_field(callback.from_user.id, 'menu', 22)

@dp.callback_query(lambda query: query.data == "woman")
async def process_settings(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.delete()
    await update_user_field(user_id, 'sex', "Женский")
    try:
        name = await get_user_field(callback.from_user.id, "name")
        sex = await get_user_field(callback.from_user.id, "sex")
        age = await get_user_field(callback.from_user.id, "age") or "не указано"
        hobby = await get_user_field(callback.from_user.id, "hobby") or "не указано"
        await callback.message.answer(f"Имя: {name}\nПол: {sex}\nВозраст: {age}\nХобби: {hobby}\n\nВыберите, что хотите изменить.", reply_markup=settings_keyboard)
        await update_user_field(callback.from_user.id, 'menu', 22)
    except Exception as e:
        await callback.answer(f"Ошибка при получении данных: {e}")
    await update_user_field(callback.from_user.id, 'menu', 322)