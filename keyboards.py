from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Новая сказка",          callback_data="new tale")],
        [InlineKeyboardButton(text="Продолжить сказку",     callback_data="continue tale")],
        [InlineKeyboardButton(text="Редактировать профиль", callback_data="settings")],
    ]
)

settings_menu_sex_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Мужской",               callback_data="man")],
        [InlineKeyboardButton(text="Женский",               callback_data="woman")],
        [InlineKeyboardButton(text="Назад",                 callback_data="back settings")],
    ]
)

settings_back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Назад",                 callback_data="back settings")],
    ]
)

settings_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Имя",                   callback_data="name")],
        [InlineKeyboardButton(text="Пол",                   callback_data="sex")],
        [InlineKeyboardButton(text="Возраст",               callback_data="age")],
        [InlineKeyboardButton(text="Хобби",                 callback_data="hobby")],
        [InlineKeyboardButton(text="Назад",                 callback_data="back main")],
    ]
)


tale_settings_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
         [InlineKeyboardButton(text="Создать",              callback_data="create")],
        [InlineKeyboardButton(text="Продолжительность",     callback_data="size")],
        [InlineKeyboardButton(text="Главный герой",         callback_data="hero")],
        [InlineKeyboardButton(text="Жанр",                  callback_data="genre")],
        [InlineKeyboardButton(text="Мораль",                callback_data="moral")],
        [InlineKeyboardButton(text="Назад",                 callback_data="back main")],
    ]
)

tale_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Придумай сам",          callback_data="Idkt")],
        [InlineKeyboardButton(text="Закончить сказку",      callback_data="back main")],
    ]
)

tale_end_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Закончить сказку",      callback_data="back main")],
    ]
)

size_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="5 миинут",              callback_data="small tale")],
        [InlineKeyboardButton(text="10 миинут",             callback_data="medium tale")],
        [InlineKeyboardButton(text="20 минут",              callback_data="large tale")],
        [InlineKeyboardButton(text="Назад",                 callback_data="back main")],
    ]
)

hero_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Я",                     callback_data="I")],
        [InlineKeyboardButton(text="Случайный герой",       callback_data="random hero")],
        [InlineKeyboardButton(text="Назад",                 callback_data="back main")],
    ]
)

genre_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Случайный жанр",        callback_data="random genre")],
        [InlineKeyboardButton(text="Назад",                 callback_data="back main")],
    ]
)

moral_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Случайная мораль",      callback_data="random genre")],
        [InlineKeyboardButton(text="Назад",                 callback_data="back main")],
    ]
)