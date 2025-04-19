from dbtools import get_user_field, get_new_tales_num, add_tale_if_not, get_tales_field, update_tales_field, add_data_to_tale, get_user_context_tale, print_table, update_user_field
from config import TEMPERATURE, client, bot, START_MESSAGE
from prompts import get_prompt
from keyboards import main_menu_keyboard, settings_menu_sex_keyboard, settings_menu_keyboard,\
size_keyboard,  hero_keyboard, genre_keyboard, moral_keyboard, tale_keyboard, tale_end_keyboard, settings_back_keyboard, tale_settings_menu_keyboard

async def get_new_menu_lvl(button: str, cur_stage = -1, tale_size = 0):
    if(button in ["start","back main","back main from settings"]):
        return "main_menu"
    if(button in ["sex"]):
        return "settings_menu_sex"
    if(button in ["man"]):
        return "settings_menu_sex_man"
    if(button in ["woman"]):
        return "settings_menu_sex_woman"
    if(button in ["name"]):
        return "settings_menu_name"
    if(button in ["age"]):
        return "settings_menu_age"
    if(button in ["hobby"]):
        return "settings_menu_hobby"
    if(button in ["settings", "back settings"]):
        return "settings_menu"
    if(button in ["new tale", "small tale", "medium tale", "large tale", "Idkm", "I", "random hero", "random genre"]):
        return "tale_settings"
    if(button in ["create", "Idkt", "continue_tale", "continue tale"]):
        if(cur_stage == tale_size):
            return "tale_end_menu"
        return "tale_menu"
    if(button in ["size"]):
        return "size_menu"
    if(button in ["hero"]):
        return "hero_menu"
    if(button in ["genre"]):
        return "genre_menu"
    if(button in ["moral"]):
        return "moral_menu"
    

async def get_menu_text(lvl: str, user_id: int, message: str, tale_size: int):
    if(lvl == "main_menu"):
        return START_MESSAGE
    
    if(lvl in ["settings_menu", "settings_menu_sex_woman", "settings_menu_sex_man"]):
        if(lvl == "settings_menu_sex_woman"):
            await update_user_field(user_id, 'sex', "Женский")
        if(lvl == "settings_menu_sex_man"):
            await update_user_field(user_id, 'sex', "Мужской")
        name = await get_user_field(user_id, "name")
        sex = await get_user_field(user_id, "sex")
        age = await get_user_field(user_id, "age") or "не указано"
        hobby = await get_user_field(user_id, "hobby") or "не указано"
        return f"Имя: {name}\nПол: {sex}\nВозраст: {age}\nХобби: {hobby}\n\nВыберите, что хотите изменить."
    
    if(lvl in ["tale_settings"]):
        tale_num = await get_user_field(user_id, "cur_tale")
        print(tale_num)
        size = await get_tales_field(tale_num, "tale_size")
        hero = await get_tales_field(tale_num, "hero") or  "Случайный"
        genre = await get_tales_field(tale_num, "genre") or  "Случайный"
        moral = await get_tales_field(tale_num, "moral") or  "Случайный"
        match size:
            case 8:
                size = "5 минут"
            case 16:
                size = "10 минут"
            case 32:
                size = "20 минут"
        return f"Продолжительность: {size}\nГлавный герой: {hero}\nЖанр: {genre}\nМораль: {moral}\n\nВыберите, что хотите изменить:"


    if(lvl == "settings_menu_sex"):
        return "Выберите ваш пол:"
    if(lvl == "settings_menu_name"):
        return "Давай знакомиться, как тебя зовут?:"
    if(lvl == "settings_menu_age"):
        return "Сколько тебе лет?:"
    if(lvl == "settings_menu_hobby"):
        return "Какие у тебя увлечения?:"
    
    if(lvl == "size_menu"):
        return "Какую сказку ты хочешь прочесть?"
    if(lvl == "hero_menu"):
        return "Кто будет главным героем в сказке?"
    if(lvl == "genre_menu"):
        return "В каком жанре будет сказка?"
    if(lvl == "moral_menu"):
        return "Какая в сказке мораль?"
    
    return ""

async def get_menu_keyboard(lvl: str):
    match lvl:
        case "main_menu":
            return main_menu_keyboard
        case "settings_menu":
            return settings_menu_keyboard
        case "settings_menu_sex":
            return settings_menu_sex_keyboard
        case "settings_menu_sex_man":
            return settings_menu_keyboard
        case "settings_menu_sex_woman":
            return settings_menu_keyboard
        case "settings_menu_age":
            return settings_back_keyboard
        case "settings_menu_name":
            return settings_back_keyboard
        case "settings_menu_hobby":
            return settings_back_keyboard
        case "tale_settings":
            return tale_settings_menu_keyboard
        case "size_menu":
            return size_keyboard
        case "hero_menu":
            return hero_keyboard
        case "genre_menu":
            return genre_keyboard
        case "moral_menu":
            return moral_keyboard
        case "tale_menu":
            return tale_keyboard
        case "tale_end_menu":
            return tale_end_keyboard
        

async def button_hendler(user_id: int, button: str):
    if(button == "new tale"):
        await update_user_field(user_id, "cur_tale", await get_new_tales_num(user_id))
    if(button == "small tale"):
        await update_tales_field(await get_user_field(user_id, "cur_tale"), "tale_size", 8)
    if(button == "medium tale"):
        await update_tales_field(await get_user_field(user_id, "cur_tale"), "tale_size", 16)
    if(button == "large tale"):
        await update_tales_field(await get_user_field(user_id, "cur_tale"), "tale_size", 32)
    if(button == "I"):
        await update_tales_field(await get_user_field(user_id, "cur_tale"), "hero", "Я")
    if(button == "Idkh"):
        await update_tales_field(await get_user_field(user_id, "cur_tale"), "hero", "Случайный")
    if(button == "Idkg"):
        await update_tales_field(await get_user_field(user_id, "cur_tale"), "genre", "Случайный")
    if(button == "Idkm"):
        await update_tales_field(await get_user_field(user_id, "cur_tale"), "moral", "Случайный")

    if(button == "Idkt" or button == "create"):
        tale_num = await get_user_field(user_id, "cur_tale")
        size = await get_tales_field(tale_num, "tale_size")
        if(await get_tales_field(tale_num, "cur_stage") == None):
            await update_tales_field(tale_num, 'cur_stage', 0)
        await add_tale_if_not(tale_num, size)
        stage = await get_tales_field(tale_num, 'cur_stage') + 1
        print(f"stage = {stage}")
        await update_tales_field(tale_num, 'cur_stage', stage)

        prompt = await get_prompt("Придумай сам, что-нибудь интересное.",user_id, tale_num);
        print(f"prompt = {prompt}")
        await add_data_to_tale(tale_num, prompt, size)
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
        if(button == "create"):
            hero = await get_tales_field(tale_num, "hero") or "НОВАЯ СКАЗКА"
            return f"========[{hero}]========\n" + bot_response
        else:
            return bot_response

    return ""
