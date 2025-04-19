from aiogram.types import CallbackQuery
from dbtools import get_user_field, update_user_field
from config import dp, bot
from menu import get_new_menu_lvl, get_menu_text, get_menu_keyboard,button_hendler
from dbtools import print_table, get_tales_field, get_user_field 

@dp.callback_query()
async def process_callback(callback: CallbackQuery):
    await print_table("users")
    await print_table("tales")
    await print_table("small_tale")

    user_id = callback.from_user.id
    button_text = callback.data
    
    if(button_text == "continue tale"):
        await callback.answer("В разработке")
        return
    
    if(button_text == "Idkt"):
        ans = await callback.message.answer("Подождите, придумываю сказку...")

    button_hendler_text = await button_hendler(user_id, button_text)
    
    cur_stage = await get_tales_field(await get_user_field(user_id, "cur_tale") or 0, "cur_stage") or 0
    print(cur_stage)
    tale_size = await get_tales_field(await get_user_field(user_id, "cur_tale") or 0, "tale_size") or 0
    print(tale_size)
    menu_lvl = await get_new_menu_lvl(button_text, cur_stage, tale_size)
    print(menu_lvl)
    print(f"menu_lvl : {menu_lvl}")
    await update_user_field(user_id, 'menu', menu_lvl)
    
    if(button_text != "Idkt" and button_text != "back main"):
        try:
            await callback.message.delete()
        except:
            print("Удаление в callback не удалось")

    if(button_text == "Idkt"):
        try:
            await bot.delete_message(chat_id=callback.message.chat.id,message_id=ans.message_id)
        except: pass

    try:
        ans = await callback.message.answer(
            button_hendler_text + await get_menu_text(lvl = menu_lvl, user_id=user_id, message=None, tale_size=None),
            reply_markup=await get_menu_keyboard(menu_lvl)
        )
        await update_user_field(user_id, 'last_message', ans.message_id)
    except:
        print("Except in callback")