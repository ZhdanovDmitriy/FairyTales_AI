from aiogram.types import CallbackQuery
from dbtools import get_user_field, update_user_field
from config import START_MESSAGE, dp, bot
from menu import get_new_menu_lvl, get_menu_text, get_menu_keyboard, button_hendler
from dbtools import fetch_current_db, check_all_users, print_table, get_tales_field, get_user_field 

@dp.callback_query()
async def process_tale(callback: CallbackQuery):
    await print_table("users")
    await print_table("tales")
    await print_table("small_tale")
    button_text = callback.data

    if(button_text == "continue tale"):
        await callback.answer("В разработке")
        
    print(f"button_text : {button_text}")
    cur_stage = await get_tales_field(await get_user_field(callback.from_user.id, "cur_tale"), "cur_stage") or 0
    tale_size = await get_tales_field(await get_user_field(callback.from_user.id, "cur_tale"), "tale_size") or 0
    menu_lvl = await get_new_menu_lvl(button_text, cur_stage, tale_size)
    button_hendler_text = await button_hendler(callback.from_user.id, button_text);
    print(f"menu_lvl : {menu_lvl}")
    await update_user_field(callback.from_user.id, 'menu', menu_lvl)

    if(button_text != "I dont know tale" and button_text != "back main from tale"):
        await callback.message.delete()
    try:
        await callback.message.answer(
            button_hendler_text + await get_menu_text(lvl = menu_lvl, user_id=callback.from_user.id, message=None, tale_size=None),
            reply_markup=await get_menu_keyboard(menu_lvl)
        )
    except:
        print("Except in callback")