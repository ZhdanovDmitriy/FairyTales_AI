from dbtools import get_user_field, get_new_tales_num, add_tale_if_not, get_tales_field, update_tales_field, add_data_to_tale, get_user_context_tale, print_table, update_user_field
from config import TEMPERATURE, client, bot, START_MESSAGE
from prompts import get_prompt
from keyboards import main_menu_keyboard, settings_menu_sex_keyboard, settings_menu_keyboard,\
size_menu_keyboard,  hero_menu_keyboard, genre_menu_keyboard, moral_menu_keyboard, tale_menu_keyboard, ultimative_settings_back, tale_end_keyboard

async def get_new_menu_lvl(button: str, cur_stage : int, tale_size: int):
    if(button in ["start","back main from settings", "back main from size", "back main from hero", "back main from genre", "back main from moral", "back main from tale"]):
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
    if(button in ["settings", "back settings from sex"]):
        return "settings_menu"
    if(button in ["new tale", "back size from hero"]):
        return "size_menu"
    if(button in ["small tale", "medium tale", "large tale", "back hero from genre"]):
        return "hero_menu"
    if(button in [ "I", "I dont know hero", "back genre from moral"]):
        return "genre_menu"
    if(button in [ "I dont know genre"]):
        return "moral_menu"
    if(button in ["I dont know tale", "I dont know moral"] and tale_size != cur_stage):
        return "tale_menu"
    else:
        return "end_tale_menu"
    
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
    if(button == "I dont know hero"):
        await update_tales_field(await get_user_field(user_id, "cur_tale"), "hero", "None")
    if(button == "I dont know genre"):
        await update_tales_field(await get_user_field(user_id, "cur_tale"), "genre", "None")
    if(button == "I dont know moral"):
        print("I dont know moral")
        tale_num = await get_user_field(user_id, "cur_tale")
        size = await get_tales_field(tale_num, "tale_size")
        if(await get_tales_field(tale_num, "cur_stage") == None):
            await update_tales_field(tale_num, 'cur_stage', 0)
        await update_tales_field(tale_num, "moral", "None")
        await add_tale_if_not(tale_num, size)
        stage = await get_tales_field(tale_num, 'cur_stage')
        print(f"stage = {stage}")
        await update_tales_field(tale_num, 'cur_stage', stage)
        prompt = await get_prompt("",user_id, tale_num);
        print(f"prompt = {prompt}")
        await add_data_to_tale(tale_num, prompt, size)
        context = await get_user_context_tale(tale_num, size)
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
        return bot_response

    if(button == "I dont know tale"):
        print("I dont know tale")
        tale_num = await get_user_field(user_id, "cur_tale")
        size = await get_tales_field(tale_num, "tale_size")
        if(get_tales_field(tale_num, "cur_stage") == None):
            await update_tales_field(tale_num, 'cur_stage', 0)
        await update_tales_field(tale_num, "moral", "None")
        await add_tale_if_not(tale_num, size)
        stage = await get_tales_field(tale_num, 'cur_stage') + 1
        print(f"stage = {stage}")
        await update_tales_field(tale_num, 'cur_stage', stage)

        prompt = await get_prompt("Придумай сам, что-нибудь интересное.",user_id, tale_num);
        print(f"prompt = {prompt}")
        await add_data_to_tale(tale_num, prompt, size)
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
        return bot_response

    return ""


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
            return ultimative_settings_back
        case "settings_menu_name":
            return ultimative_settings_back
        case "settings_menu_hobby":
            return ultimative_settings_back
        case "size_menu":
            return size_menu_keyboard
        case "hero_menu":
            return hero_menu_keyboard
        case "genre_menu":
            return genre_menu_keyboard
        case "moral_menu":
            return moral_menu_keyboard
        case "tale_menu":
            return tale_menu_keyboard
        case "end_tale_menu":
            return tale_end_keyboard
'''

async def get_continue_num(lvl: str):
'''


'''

async def get_last_menu_lvl(button: str):
    if(button in ["new tale", "settings", "continue tale"]):
        return "main_menu"
    if(button in ["man", "woman", "back settings from sex"]):
        return "settings_menu_sex"
    if(button in ["name", "sex", "age", "hobby", "back main from settings"]):
        return "settings_menu"
    if(button in ["small tale", "medium tale", "large tale", "back main from size"]):
        return "size_menu"
    if(button in ["I", "I dont know hero", "back size from hero", "back main from hero"]):
        return "hero_menu"
    if(button in ["I dont know genre", "back hero from genre", "back main from genre"]):
        return "genre_menu"
    if(button in ["I dont know moral", "back genre from moral", "back main from moral"]):
        return "moral_menu"
    if(button in ["I dont know tale", "back main from tale"]):
        return "tale_menu"
    
'''