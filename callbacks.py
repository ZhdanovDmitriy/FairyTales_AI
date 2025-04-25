from aiogram.types import CallbackQuery, FSInputFile
from dbtools import get_user_field, update_user_field
from config import bot, router, START_MESSAGE
from aiogram import F
from menu import get_new_menu_lvl, get_menu_text, get_menu_keyboard,button_hendler
from dbtools import print_table, get_tales_field, get_user_field, get_parts_tale

@router.callback_query(F.data == "continue tale")
async def continue_tale_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    cur_tale = await get_user_field(user_id, "cur_tale")
    try:
        parts = await get_parts_tale(cur_tale , await get_tales_field(cur_tale, "tale_size"))
    except:pass
    if(cur_tale == 0 or parts == None):
        await callback.answer("У вас нет начатой сказки!")
        return
    try:
        await callback.message.delete()
    except:
        print("Удаление в callback не удалось")
    hero = await get_tales_field(cur_tale, "hero") or "ПРОДОЛЖЕНИЕ"
    await callback.message.answer(f"========[{hero}]========\n")
    for part in parts[:-1]:
        await callback.message.answer(part, parse_mode="Markdown")
    await update_user_field(user_id, 'menu', "tale_menu")
    await callback.message.answer(parts[-1], parse_mode="Markdown", reply_markup=await get_menu_keyboard("tale_menu"))

@router.callback_query()
async def process_callback(callback: CallbackQuery):
    await print_table("users")
    await print_table("tales")
    await print_table("small_tale")

    user_id = callback.from_user.id
    button_text = callback.data
    
    if(button_text == "Idkt" or button_text == "create"):
        ans = await callback.message.answer('''Секундочку — проверяю, не забыл ли я добавить щепотку волшебства! 💫\n\n*Подсказка*:\nПопробуй отвечать развёрнуто — так сказка станет интереснее! ✨ ''', parse_mode="Markdown")

    button_hendler_text = await button_hendler(user_id, button_text)
    
    cur_stage = await get_tales_field(await get_user_field(user_id, "cur_tale") or 0, "cur_stage") or 0
    print(cur_stage)
    tale_size = await get_tales_field(await get_user_field(user_id, "cur_tale") or 0, "tale_size") or 0
    print(tale_size)
    menu_lvl = await get_new_menu_lvl(button_text, cur_stage, tale_size)
    print(menu_lvl)
    print(f"menu_lvl : {menu_lvl}")
    await update_user_field(user_id, 'menu', menu_lvl)
    
    if (button_text != "Idkt" and button_text != "back main"):
        try:
            await callback.message.delete()
        except:
            print("Удаление в callback не удалось")

    if (button_text == "Idkt" or button_text == "create"):
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
    except:
        print("Except in callback")