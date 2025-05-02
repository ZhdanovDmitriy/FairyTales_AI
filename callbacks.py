from aiogram.types import CallbackQuery, FSInputFile
from dbtools import get_user_field, update_user_field
from config import bot, router, START_MESSAGE, LINK
from aiogram import F
from menu import get_new_menu_lvl, get_menu_text, get_menu_keyboard,button_hendler
from dbtools import get_tales_field, get_user_field, get_parts_tale
from keyboards import tale_end_keyboard
from prompts import get_stub_message
from logger import log_event, get_db_state

@router.callback_query(F.data == "continue tale")
async def continue_tale_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    cur_tale = await get_user_field(user_id, "cur_tale")
    size = await get_tales_field(cur_tale, "tale_size")
    cur_stage = await get_tales_field(cur_tale, "cur_stage")
    
    # Логируем получение данных
    await log_event(user_id, callback.data, "Запрос на продолжение сказки", await get_db_state(user_id))

    try:
        parts = await get_parts_tale(cur_tale , size)
    except: pass
    if cur_tale == 0 or parts is None:
        await callback.answer("У вас нет начатой сказки!")
        await log_event(user_id, callback.data, "Нет начатой сказки", await get_db_state(user_id))
        return
    
    try:
        await callback.message.delete()
    except:
        print("Удаление в callback не удалось")

    await callback.message.answer( "\u00A0" * 19 + "🎉 *Продолжение* 🎉" + "\u00A0" * 14, parse_mode="Markdown")
    for part in parts[:-1]:
        await callback.message.answer(part, parse_mode="Markdown")
    await update_user_field(user_id, 'menu', "tale_menu")
    
    if cur_stage == size:
        await callback.message.answer(parts[-1], parse_mode="Markdown", reply_markup=tale_end_keyboard)
    else:
        await callback.message.answer(parts[-1], parse_mode="Markdown", reply_markup=await get_menu_keyboard("tale_menu"))

    # Логируем отправку сообщения с продолжением
    await log_event(user_id, callback.data, "Сообщение с продолжением сказки", await get_db_state(user_id))

@router.callback_query()
async def process_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    button_text = callback.data
    
    # Логируем нажатие кнопки
    await log_event(user_id, button_text, "Нажата кнопка", await get_db_state(user_id))

    if button_text not in ["Idkt", "back main"]:
        try:
            await callback.message.delete()
        except:
            print("Удаление в callback не удалось")

    if button_text == "Idkt" or button_text == "create":
        ans = await callback.message.answer(f"{await get_stub_message()}\n\n*Подсказка*:\nПопробуй отвечать развёрнуто — так сказка станет интереснее! ✨ ", parse_mode="Markdown")
    
    button_hendler_text = await button_hendler(user_id, button_text)
    
    cur_stage = await get_tales_field(await get_user_field(user_id, "cur_tale") or 0, "cur_stage") or 0
    print(cur_stage)
    tale_size = await get_tales_field(await get_user_field(user_id, "cur_tale") or 0, "tale_size") or 0
    print(tale_size)
    menu_lvl = await get_new_menu_lvl(button_text, cur_stage, tale_size)
    print(menu_lvl)
    print(f"menu_lvl : {menu_lvl}")
    await update_user_field(user_id, 'menu', menu_lvl)

    if button_text == "Idkt" or button_text == "create":
        try:
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=ans.message_id)
        except:
            print("Удаление в callback не удалось")

    try:
        if await get_menu_text(lvl=menu_lvl, user_id=user_id) == START_MESSAGE:
            ans = await callback.message.answer_photo(
                FSInputFile("source/Start_image.jpg"),
                caption=button_hendler_text + await get_menu_text(lvl=menu_lvl, user_id=user_id),
                parse_mode="Markdown",
                reply_markup=await get_menu_keyboard(menu_lvl)
            )
        else:
            ans = await callback.message.answer(
                button_hendler_text + await get_menu_text(lvl=menu_lvl, user_id=user_id),
                parse_mode="Markdown",
                reply_markup=await get_menu_keyboard(menu_lvl)
            )
        await update_user_field(user_id, 'last_message', ans.message_id)
        
        # Логируем отправку сообщения
        await log_event(user_id, button_text, "Отправлено сообщение", await get_db_state(user_id))

    except:
        print("Except in callback")

    # Удалить в release версии
    if button_text == "Idkt" and cur_stage == tale_size:
        ans = await callback.message.answer(f"\nКонец!\nЯ очень рад, что ты побывал в моей сказке!\n\nСейчас я учусь рассказывать истории ещё интереснее, и твоя помощь мне очень нужна! Если тебе понравилось это приключение или ты хочешь что-то изменить — скажи мне!\n\nЗаполни эту [форму]({LINK}) и благодаря тебе я стану лучше✨\n\n_Рекомендую впервые заполнить её через 2-3 истории_\n\nСпасибо, что помогаешь мне создавать самые лучшие сказки на свете! 💙", parse_mode="Markdown", reply_markup=tale_end_keyboard)
        
        # Логируем завершение сказки
        await log_event(user_id, button_text, "Сказка завершена", await get_db_state(user_id))
        return