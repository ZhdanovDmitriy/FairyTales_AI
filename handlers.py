import asyncio
from aiogram import types
from datetime import datetime
from aiogram.filters import Command
from aiogram.types import Message
from dbtools import add_user, update_user_field, get_user_field, add_tale_if_not, \
    add_data_to_tale, get_user_context_tale, get_tales_field,  update_tales_field, print_table
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
        await update_tales_field(user_id, 'hero', message.text)
        await update_user_field(user_id, 'menu', "genre_menu")
        await message.answer(
                await get_menu_text(lvl = "genre_menu",user_id=user_id, message=None, tale_size=None),
                reply_markup=await get_menu_keyboard("genre_menu")
        )

    if await get_user_field(user_id, "menu") == "genre_menu":
        if len(message.text) > 300:
            msg = await message.answer("Я уже забыл, что ты говорил в начале.\nМожет быть ты сможешь сократить рассказ?")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return
        await update_tales_field(user_id, 'genre', message.text)
        await update_user_field(user_id, 'menu', "moral_menu")
        await message.answer(
                await get_menu_text(lvl = "moral_menu",user_id=user_id, message=None, tale_size=None),
                reply_markup=await get_menu_keyboard("moral_menu")
        )


    if await get_user_field(user_id, "menu") == "moral_menu":
        if len(message.text) > 300:
            msg = await message.answer("Я уже забыл, что ты говорил в начале.\nМожет быть ты сможешь сократить рассказ?")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return
        
        print("handler moral")
        await update_tales_field(user_id, 'moral', message.text)
        await update_user_field(user_id, 'menu', "tale_menu")
        tale_num = await get_user_field(user_id, "cur_tale")
        size = await get_tales_field(tale_num, "tale_size")
        if(get_tales_field(tale_num, "cur_stage") == None):
            await update_tales_field(tale_num, 'cur_stage', 0)
        await update_tales_field(tale_num, "moral", "None")
        await add_tale_if_not(tale_num, size)
        stage = await get_tales_field(tale_num, 'cur_stage')
        print(f"stage = {stage}")
        await update_tales_field(tale_num, 'cur_stage', stage)
        prompt = await get_prompt("", user_id, tale_num);
        print(f"prompt = {prompt}")
        await add_data_to_tale(tale_num, prompt, size)
        context = await get_user_context_tale(tale_num, size)
        msg = await message.answer("Придумываю сказку...")
        """
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=context,
            stream=False,
            temperature=TEMPERATURE,
            parallel_tool_calls = True
        )
        bot_response = response.choices[0].message.content
        """
        bot_response="smth"
        await add_data_to_tale(tale_num, bot_response, size)
        await print_table("tales")
        await print_table("small_tale")

        await msg.delete()
        await message.answer(bot_response, reply_markup=await get_menu_keyboard("tale_menu"))

    if await get_user_field(user_id, "menu") == "tale_menu":
        if len(message.text) > 300:
            msg = await message.answer("Я уже забыл, что ты говорил в начале.\nМожет быть ты сможешь сократить рассказ?")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return
        
        print("handler tale")
        await update_tales_field(user_id, 'menu', "tale_menu")
        tale_num = await get_user_field(user_id, "cur_tale")
        size = await get_tales_field(tale_num, "tale_size")
        if(get_tales_field(tale_num, "cur_stage") == None):
            await update_tales_field(tale_num, 'cur_stage', 0)
        await update_tales_field(tale_num, "moral", "None")
        await add_tale_if_not(tale_num, size)
        stage = await get_tales_field(tale_num, 'cur_stage') + 1
        print(f"stage = {stage}")
        await update_tales_field(tale_num, 'cur_stage', stage)
        prompt = await get_prompt(message.text, user_id, tale_num);
        print(f"prompt = {prompt}")
        await add_data_to_tale(tale_num, prompt, size)
        context = await get_user_context_tale(tale_num, size)
        msg = await message.answer("Придумываю сказку...")
        """
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=context,
            stream=False,
            temperature=TEMPERATURE,
            parallel_tool_calls = True
        )
        bot_response = response.choices[0].message.content
        """
        bot_response="smth"
        await add_data_to_tale(tale_num, bot_response, size)
        await print_table("tales")
        await print_table("small_tale")

        await msg.delete()
        if(stage == size):
            await message.answer(bot_response + "Конец!\n**Ссылка на форму обратной связи**", reply_markup=tale_end_keyboard)
        await message.answer(bot_response, reply_markup=await get_menu_keyboard("tale_menu"))
    

'''
    if await get_user_field(user_id, "menu") == 324:
        if len(message.text) > 500:
            msg = await message.answer("Я не смоуг столько запомнить. Пожалуйста, сократите свой рассказ хотя бы до 500 символов.")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return
        
        await update_user_field(user_id, 'hobby', message.text)
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
            name = await get_user_field(user_id, "name")
            sex = await get_user_field(user_id, "sex")
            age = await get_user_field(user_id, "age") or "не указано"
            hobby = await get_user_field(user_id, "hobby") or "не указано"
            await message.answer(f"Имя: {name}\nПол: {sex}\nВозраст: {age}\nХобби: {hobby}\n\nВыберите, что хотите изменить.", reply_markup=settings_keyboard)
            await update_user_field(user_id, 'menu', 22)
        except Exception as e:
            await message.answer(f"Ошибка при получении данных: {e}")

    if await get_user_field(user_id, "menu") == 325:
        if len(message.text) > 50:
            msg = await message.answer("Я не могу поверить, что у тебя такое сложное имя.\nМожет быть у тебя есть более краткая форма имени?")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return
        
        await update_user_field(user_id, 'name', message.text)
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
            name = await get_user_field(user_id, "name")
            sex = await get_user_field(user_id, "sex")
            age = await get_user_field(user_id, "age") or "не указано"
            hobby = await get_user_field(user_id, "hobby") or "не указано"
            await message.answer(f"Имя: {name}\nПол: {sex}\nВозраст: {age}\nХобби: {hobby}\n\nВыберите, что хотите изменить.", reply_markup=settings_keyboard)
            await update_user_field(user_id, 'menu', 22)
        except Exception as e:
            await message.answer(f"Ошибка при получении данных: {e}")

    if await get_user_field(user_id, "menu") == 311:
        tale_num = await get_tale_num(user_id, 8, 0, "0")
        await add_small_tale_if_not(tale_num)
        stage = await get_tale_field(tale_num, 'cur_stage') + 1
        if(stage == 1):
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
        print(f"stage = {stage}")
        await update_tale_field(tale_num, 'cur_stage', stage)
        text = message.text
        name = await get_user_field(user_id, "name") or "не указано"
        sex = await get_user_field(user_id, "sex") or "не указано"
        age = await get_user_field(user_id, "age") or "не указано"
        hobby = await get_user_field(user_id, "hobby") or "не указано"
        prompt = await get_prompt(text, name, sex, age, hobby, await get_tale_field(tale_num, 'genre'), stage, await get_tale_field(tale_num, 'tale_size'));
        print(f"prompt = {prompt}")
        await add_data_to_small_tale(tale_num, prompt)
        context = await get_user_context_small_tale(tale_num)
        placeholder = await message.answer("Подождите, придумываю сказку...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=context,
            stream=False,
            temperature=TEMPERATURE,
            parallel_tool_calls = True
        )
        bot_response = response.choices[0].message.content
        await add_data_to_small_tale(tale_num, bot_response)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message(chat_id=message.chat.id, message_id=placeholder.message_id)
        await print_table("tales")
        await print_table("small_tale")
        if stage >= 8:
            await message.answer(bot_response + "\nКонец!")
            await message.answer("Сказка подошла к концу, хочешь увидеть еще одну?", reply_markup=genre_keyboard)
        else:
            await message.answer(bot_response)

            '''