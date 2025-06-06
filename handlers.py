import asyncio
from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message
from dbtools import add_user, update_user_field, get_user_field, add_tale_if_not, \
    add_data_to_tale, get_tales_field,  update_tales_field, print_table, get_user_context_tale, is_user_exists
from config import START_MESSAGE, TEMPERATURE, client, bot, dp, LINK
from prompts import get_prompt, get_stub_message
from menu import get_menu_text, get_menu_keyboard
from keyboards import main_menu_keyboard, tale_end_keyboard
from logger import log_event, get_db_state
import re

clean_pattern = re.compile(r'[^a-zA-Zа-яА-ЯёЁ0-9 .,;:\'\"\-?/]+')

@dp.message()
async def chat_handler(message: types.Message):
    user_id = message.from_user.id

    if(not await is_user_exists(user_id)):
        await add_user(user_id, "не указано", None, "не указано", None, "не указано", message.message_id)#Добавляет нового пользователя и сбрасывает все параметры по умолчанию
        await message.answer_photo(types.FSInputFile("source/Start_image.jpg"), caption=START_MESSAGE, reply_markup=main_menu_keyboard)
        await update_user_field(user_id, 'menu', "main_menu")

        # Логируем реакцию бота
        await log_event(user_id, "отправлено сообщение до внесения в бд", "Отправлено стартовое сообщение", await get_db_state(user_id))
        return 
    
    if message.text == None:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        print(f"[EXCEPT] Пользователь {user_id} отправил нераспознанное сообщение")
        return
    user_message = clean_pattern.sub('', message.text)
    if user_message == "":
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        print(f"[EXCEPT] Пользователь {user_id} отправил нераспознанное сообщение")
        return

    if await get_user_field(user_id, "process") == "yes":
        msg = await message.answer("Подожди немного, осталось чуть-чуть!☄️", parse_mode="Markdown")
        await asyncio.sleep(3)
        await msg.delete()
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        print(f"[EXCEPT] Пользователь {user_id} попытался отправить сообщение во время генерации сказки")
        return

    await log_event(user_id, user_message, "Получено сообщение", await get_db_state(user_id))

    if user_message == "/start":
        await add_user(user_id, "не указано", None, "не указано", None, "не указано", message.message_id)#Добавляет нового пользователя и сбрасывает все параметры по умолчанию
        await message.answer_photo(types.FSInputFile("source/Start_image.jpg"), caption=START_MESSAGE, reply_markup=main_menu_keyboard)
        await update_user_field(user_id, 'menu', "main_menu")

        # Логируем реакцию бота
        await log_event(user_id, user_message, "Отправлено стартовое сообщение", await get_db_state(user_id))
        return

    elif await get_user_field(user_id, "menu") == "settings_menu_age":  
        try:
            if int(user_message) < 0 or int(user_message) > 100 :
                msg = await message.answer("😯Мне кажется, ты где-то лукавишь!\nПожалуйста, введи свой настоящий возраст.", parse_mode="Markdown")
                await asyncio.sleep(3)
                await msg.delete()
                await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                return
            age_value = int(user_message)
            await update_user_field(user_id, 'age', age_value)
            await update_user_field(user_id, 'menu', "settings_menu")
            
            try:
                await bot.delete_message(chat_id=message.chat.id, message_id=await get_user_field(message.from_user.id, "last_message"))
                await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            except:
                print("[EXCEPT] Удаление в handlers не удалось")

            await message.answer(await get_menu_text(lvl="settings_menu", user_id=user_id), parse_mode="Markdown", reply_markup=await get_menu_keyboard("settings_menu"))
            
            # Логируем успешное обновление возраста
            await log_event(user_id, user_message, "Возраст обновлен", await get_db_state(user_id))

        except ValueError:
            msg = await message.answer("Дорогой друг, давай будем посерьезнее😉\nВведи число, пожалуйста!", parse_mode="Markdown")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            
            # Логируем ошибку в возрасте
            await log_event(user_id, user_message, "Ошибка ввода возраста", await get_db_state(user_id))
            return
        return
    
    elif await get_user_field(user_id, "menu") == "settings_menu_hobby":
        if len(user_message) > 500:
            msg = await message.answer("Я не смоуг столько запомнить. Пожалуйста, сократите свой рассказ хотя бы до 500 символов.", parse_mode="Markdown")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return
        await update_user_field(user_id, 'hobby', user_message)
        await update_user_field(user_id, 'menu', "settings_menu")

        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=await get_user_field(message.from_user.id,"last_message"))
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except:
            print("[EXCEPT] Удаление в handlers не удалось")

        await message.answer(await get_menu_text(lvl="settings_menu", user_id=user_id), parse_mode="Markdown", reply_markup=await get_menu_keyboard("settings_menu"))

        # Логируем успешное обновление хобби
        await log_event(user_id, user_message, "Хобби обновлено", await get_db_state(user_id))
        return
    
    elif await get_user_field(user_id, "menu") == "settings_menu_name":
        if len(user_message) > 50:
            msg = await message.answer("Я не могу поверить, что у тебя такое сложное имя.\nМожет быть у тебя есть более краткая форма имени?", parse_mode="Markdown")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return
        
        await update_user_field(user_id, 'name', user_message)
        await update_user_field(user_id, 'menu', "settings_menu")
        
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=await get_user_field(message.from_user.id,"last_message"))
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except:
            print("[EXCEPT] Удаление в handlers не удалось")

        await message.answer(await get_menu_text(lvl="settings_menu", user_id=user_id), parse_mode="Markdown", reply_markup=await get_menu_keyboard("settings_menu"))

        # Логируем успешное обновление имени
        await log_event(user_id, user_message, "Имя обновлено", await get_db_state(user_id))
        return
    
    elif await get_user_field(user_id, "menu") == "hero_menu":
        if len(user_message) > 300:
            msg = await message.answer("Я уже забыл, что ты говорил в начале.\nМожет быть ты сможешь сократить рассказ?", parse_mode="Markdown")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return
        await update_tales_field(await get_user_field(user_id, "cur_tale"), 'hero', user_message)
        await update_user_field(user_id, 'menu', "hero_menu")

        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=await get_user_field(message.from_user.id,"last_message"))
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except:
            print("[EXCEPT] Удаление в handlers не удалось")

        await message.answer(await get_menu_text(lvl="tale_settings", user_id=user_id), parse_mode="Markdown", reply_markup=await get_menu_keyboard("tale_settings"))

        # Логируем успешное обновление героя
        await log_event(user_id, user_message, "Герой обновлен", await get_db_state(user_id))
        return
    
    elif await get_user_field(user_id, "menu") == "genre_menu":
        if len(user_message) > 300:
            msg = await message.answer("Я уже забыл, что ты говорил в начале.\nМожет быть ты сможешь сократить рассказ?", parse_mode="Markdown")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return
        await update_tales_field(await get_user_field(user_id, "cur_tale"), 'genre', user_message)
        await update_user_field(user_id, 'menu', "genre_menu")

        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=await get_user_field(message.from_user.id,"last_message"))
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except:
            print("[EXCEPT] Удаление в handlers не удалось")
        
        await message.answer(await get_menu_text(lvl="tale_settings", user_id=user_id), parse_mode="Markdown", reply_markup=await get_menu_keyboard("tale_settings"))

        # Логируем успешное обновление жанра
        await log_event(user_id, user_message, "Жанр обновлен", await get_db_state(user_id))
        return
    
    elif await get_user_field(user_id, "menu") == "moral_menu":
        if len(user_message) > 300:
            msg = await message.answer("Я уже забыл, что ты говорил в начале.\nМожет быть ты сможешь сократить рассказ?", parse_mode="Markdown")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return
        
        await update_tales_field(await get_user_field(user_id, "cur_tale"), 'moral', user_message)
        await update_user_field(user_id, 'menu', "moral_menu")

        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=await get_user_field(message.from_user.id,"last_message"))
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except:
            print("[EXCEPT] Удаление в handlers не удалось")
        
        await message.answer(await get_menu_text(lvl="tale_settings", user_id=user_id), parse_mode="Markdown", reply_markup=await get_menu_keyboard("tale_settings"))

        # Логируем успешное обновление морали
        await log_event(user_id, user_message, "Мораль обновлена", await get_db_state(user_id))
        return
    
    elif await get_user_field(user_id, "menu") == "tale_menu":
        await update_user_field(user_id, 'process', "yes")
        tale_num = await get_user_field(user_id, "cur_tale")
        size = await get_tales_field(tale_num, "tale_size")
        if(await get_tales_field(tale_num, "cur_stage") == None):
            await update_tales_field(tale_num, 'cur_stage', 0)
        await add_tale_if_not(tale_num, size)
        stage = await get_tales_field(tale_num, 'cur_stage')

        if len(user_message) > 500:
            msg = await message.answer("Я уже забыл, что ты говорил в начале.\nМожет быть ты сможешь сократить рассказ?", parse_mode="Markdown")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            await update_user_field(user_id, 'process', "no")
            return
        
        if(stage >= size):
            msg = await message.answer("Твоя сказка подошла к концу!\nТы можешь закончить эту сказку и начать новую!", parse_mode="Markdown")
            await asyncio.sleep(3)
            await msg.delete()
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            await update_user_field(user_id, 'process', "no")
            return

        stage = stage + 1
        print(f"stage = {stage}")
        await update_tales_field(tale_num, 'cur_stage', stage)

        prompt = await get_prompt(user_message, user_id, tale_num)
        await add_data_to_tale(tale_num, prompt, size)
        msg = await message.answer(await get_stub_message(), parse_mode="Markdown")
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=await get_user_context_tale(tale_num, size),
            stream=False,
            temperature=TEMPERATURE,
            parallel_tool_calls=True
        )
        bot_response = response.choices[0].message.content
        await message.delete()
        await msg.delete()
        
        await add_data_to_tale(tale_num, bot_response, size)
        await print_table("tales")
        await print_table("small_tale")

        if(stage == size):
            await message.answer(bot_response, parse_mode="Markdown", reply_markup=tale_end_keyboard)
            #Удалить в release версии
            await message.answer(f"\nКонец!\nЯ очень рад, что ты побывал в моей сказке!\n\nСейчас я учусь рассказывать истории ещё интереснее, и твоя помощь мне очень нужна! Если тебе понравилось это приключение или ты хочешь что-то изменить — скажи мне!\n\nЗаполни эту [форму]({LINK}) и благодаря тебе я стану лучше✨\n\n_Рекомендую впервые заполнить её через 2-3 истории_\n\nСпасибо, что помогаешь мне создавать самые лучшие сказки на свете! 💙",parse_mode="Markdown", reply_markup=tale_end_keyboard)
            # Логируем завершение сказки
            await log_event(user_id, user_message, "Сказка завершена", await get_db_state(user_id))
        else:
            await message.answer(bot_response, parse_mode="Markdown", reply_markup=await get_menu_keyboard("tale_menu"))
            
            # Логируем продолжающуюся сказку
            await log_event(user_id, user_message, "Продолжение сказки", await get_db_state(user_id))

        await update_user_field(user_id, 'process', "no")
        return
    
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except:
        print("[EXCEPT] Не удалось удалить необработанное сообщение пользователя")