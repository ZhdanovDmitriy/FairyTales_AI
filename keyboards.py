from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Сказка", callback_data="tale"),
            InlineKeyboardButton(text="Настройки", callback_data="settings"),
        ]
    ],
    row_width=2,
)

sex_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Мужской", callback_data="man"),
            InlineKeyboardButton(text="Женский", callback_data="woman"),
        ]
    ],
    row_width=2,
)

back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад", callback_data="back"),
        ]
    ],
    row_width=1,
)
settings_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Имя", callback_data="name")],
        [InlineKeyboardButton(text="Пол", callback_data="sex")],
        [InlineKeyboardButton(text="Возраст", callback_data="age")],
        [InlineKeyboardButton(text="Хобби", callback_data="hobby")],
        [InlineKeyboardButton(text="Назад", callback_data="back")],
    ]
)


genre_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Хармон",       callback_data="small_tale")],
        [InlineKeyboardButton(text="В разработке", callback_data="medium_tale")],
        [InlineKeyboardButton(text="В разработке", callback_data="large_tale")],
        [InlineKeyboardButton(text="Назад",         callback_data="back")],
    ]
)