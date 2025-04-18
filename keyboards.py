from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Редактировать профиль", callback_data="settings")],
        [InlineKeyboardButton(text="Новая сказка", callback_data="new tale")],
        [InlineKeyboardButton(text="Продолжить сказку", callback_data="continue tale")],
    ]
)

settings_menu_sex_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Мужской", callback_data="man")],
        [InlineKeyboardButton(text="Женский", callback_data="woman")],
        [InlineKeyboardButton(text="Назад", callback_data="back settings from sex")],
    ]
)

settings_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Имя", callback_data="name")],
        [InlineKeyboardButton(text="Пол", callback_data="sex")],
        [InlineKeyboardButton(text="Возраст", callback_data="age")],
        [InlineKeyboardButton(text="Хобби", callback_data="hobby")],
        [InlineKeyboardButton(text="Назад", callback_data="back main from settings")],
    ]
)

size_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Маленькая(5 миинут)",       callback_data="small tale")],
        [InlineKeyboardButton(text="Средняя(10 миинут)", callback_data="medium tale")],
        [InlineKeyboardButton(text="Большая(20 минут)", callback_data="large tale")],
        [InlineKeyboardButton(text="Назад",         callback_data="back main from size")],
    ]
)

hero_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Я", callback_data="I")],
        [InlineKeyboardButton(text="Я не знаю",       callback_data="I dont know hero")],
        [InlineKeyboardButton(text="Назад", callback_data="back size from hero")],
        [InlineKeyboardButton(text="Вернуться в меню",         callback_data="back main from hero")],
    ]
)

genre_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Я не знаю",       callback_data="I dont know genre")],
        [InlineKeyboardButton(text="Назад", callback_data="back hero from genre")],
        [InlineKeyboardButton(text="Вернуться в меню",         callback_data="back main from genre")],
    ]
)

moral_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Я не знаю",       callback_data="I dont know moral")],
        [InlineKeyboardButton(text="Назад", callback_data="back genre from moral")],
        [InlineKeyboardButton(text="Вернуться в меню",         callback_data="back main from moral")],
    ]
)

tale_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Я не знаю",       callback_data="I dont know tale")],
        [InlineKeyboardButton(text="Вернуться в меню",         callback_data="back main from tale")],
    ]
)

ultimative_settings_back = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад", callback_data="back settings from sex"),
        ]
    ]
)

tale_end_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Вернуться в меню", callback_data="back main from tale"),
        ]
    ]
)