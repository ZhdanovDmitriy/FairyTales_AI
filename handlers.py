import asyncio
from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message
from dbtools import add_user, update_user_field, get_user_field, add_tale_if_not, \
    add_data_to_tale, get_tales_field,  update_tales_field, print_table, get_user_context_tale
from config import START_MESSAGE, TEMPERATURE, client, bot, dp
from prompts import get_prompt
from menu import get_menu_text, get_menu_keyboard
from keyboards import main_menu_keyboard, tale_end_keyboard

@dp.message()
async def chat_handler(message: types.Message):
    user_id = message.from_user.id
    if(message.text == "/start"):
        await add_user(user_id, "не указано", None, "не указано", None, "не указано", message.message_id)
        await message.answer(START_MESSAGE, reply_markup=main_menu_keyboard)
        await update_user_field(user_id, 'menu', "main_menu")
    
    if await get_user_field(user_id, "menu") == "settings_menu_age":
        try:
            age_value = abs(int(message.text))%100
            await update_user_field(user_id, 'age', age_value)
            await update_user_field(user_id, 'menu', "settings_menu")
            try:
                await bot.delete_message(chat_id=message.chat.id, message_id=await get_user_field(message.from_user.id,"last_message"))
                await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            except: pass
            await message.answer(
                await get_menu_text(lvl = "settings_menu",user_id=user_id, message=None, tale_size=None),
                reply_markup=await get_menu_keyboard("settings_menu")
            )
        except ValueError:
            msg = await message.answer("Некорректное значение возраста, введите число.")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return

    if await get_user_field(user_id, "menu") == "settings_menu_hobby":
        if len(message.text) > 500:
            msg = await message.answer("Я не смоуг столько запомнить. Пожалуйста, сократите свой рассказ хотя бы до 500 символов.")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return
        await update_user_field(user_id, 'hobby', message.text)
        await update_user_field(user_id, 'menu', "settings_menu")
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=await get_user_field(message.from_user.id,"last_message"))
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except: pass
        await message.answer(
                await get_menu_text(lvl = "settings_menu",user_id=user_id, message=None, tale_size=None),
                reply_markup=await get_menu_keyboard("settings_menu")
        )

    if await get_user_field(user_id, "menu") == "settings_menu_name":
        if len(message.text) > 50:
            msg = await message.answer("Я не могу поверить, что у тебя такое сложное имя.\nМожет быть у тебя есть более краткая форма имени?")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return
        
        await update_user_field(user_id, 'name', message.text)
        await update_user_field(user_id, 'menu', "settings_menu")
        
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=await get_user_field(message.from_user.id,"last_message"))
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except: pass

        await message.answer(
                await get_menu_text(lvl = "settings_menu",user_id=user_id, message=None, tale_size=None),
                reply_markup=await get_menu_keyboard("settings_menu")
        )

    if await get_user_field(user_id, "menu") == "hero_menu":
        if len(message.text) > 300:
            msg = await message.answer("Я уже забыл, что ты говорил в начале.\nМожет быть ты сможешь сократить рассказ?")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return
        await update_tales_field(await get_user_field(user_id, "cur_tale"), 'hero', message.text)
        await update_user_field(user_id, 'menu', "hero_menu")

        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=await get_user_field(message.from_user.id,"last_message"))
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except: pass

        await message.answer(
                await get_menu_text(lvl = "tale_settings",user_id=user_id, message=None, tale_size=None),
                reply_markup=await get_menu_keyboard("tale_settings")
        )

    if await get_user_field(user_id, "menu") == "genre_menu":
        if len(message.text) > 300:
            msg = await message.answer("Я уже забыл, что ты говорил в начале.\nМожет быть ты сможешь сократить рассказ?")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return
        await update_tales_field(await get_user_field(user_id, "cur_tale"), 'genre', message.text)
        await update_user_field(user_id, 'menu', "genre_menu")
        
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=await get_user_field(message.from_user.id,"last_message"))
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except: pass
        
        await message.answer(
                await get_menu_text(lvl = "tale_settings",user_id=user_id, message=None, tale_size=None),
                reply_markup=await get_menu_keyboard("tale_settings")
        )


    if await get_user_field(user_id, "menu") == "moral_menu":
        if len(message.text) > 300:
            msg = await message.answer("Я уже забыл, что ты говорил в начале.\nМожет быть ты сможешь сократить рассказ?")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return
        
        await update_tales_field(await get_user_field(user_id, "cur_tale"), 'moral', message.text)
        await update_user_field(user_id, 'menu', "moral_menu")

        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=await get_user_field(message.from_user.id,"last_message"))
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except: pass
        
        await message.answer(
                await get_menu_text(lvl = "tale_settings",user_id=user_id, message=None, tale_size=None),
                reply_markup=await get_menu_keyboard("tale_settings")
        )


    if await get_user_field(user_id, "menu") == "tale_menu":
        if len(message.text) > 500:
            msg = await message.answer("Я уже забыл, что ты говорил в начале.\nМожет быть ты сможешь сократить рассказ?")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return

        tale_num = await get_user_field(user_id, "cur_tale")
        size = await get_tales_field(tale_num, "tale_size")
        if(await get_tales_field(tale_num, "cur_stage") == None):
            await update_tales_field(tale_num, 'cur_stage', 0)
        await add_tale_if_not(tale_num, size)
        stage = await get_tales_field(tale_num, 'cur_stage') + 1
        print(f"stage = {stage}")
        await update_tales_field(tale_num, 'cur_stage', stage)

        prompt = await get_prompt(message.text,user_id, tale_num);
        print(f"prompt = {prompt}")
        await add_data_to_tale(tale_num, prompt, size)
        msg = await message.answer("Придумываю сказку...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=await get_user_context_tale(tale_num, size),
            stream=False,
            temperature=TEMPERATURE,
            parallel_tool_calls = True
        )
        bot_response = response.choices[0].message.content
        await add_data_to_tale(tale_num, bot_response, size)
        await print_table("tales")
        await print_table("small_tale")

        await message.delete()
        await msg.delete()
        if(stage == size):
            await message.answer(bot_response + "\nКонец!\n**Ссылка на форму обратной связи**", reply_markup=tale_end_keyboard)
        else:
            await message.answer(bot_response, reply_markup=await get_menu_keyboard("tale_menu"))
        
