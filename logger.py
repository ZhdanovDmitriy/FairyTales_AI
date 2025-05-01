import aiofiles
from datetime import datetime
import json
from typing import Any
from dbtools import get_user_field, get_tales_num, get_new_tales_num, return_fail_value, get_tales_field, get_parts_tale, get_user_context_tale

LOG_FILE = "bot.log"

async def log_event(user_id: int, message: str, reaction: str, db_diff: Any = None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = {
        "time": timestamp,
        "user_id": user_id,
        "message": message,
        "reaction": reaction,
        "db_changes": db_diff
    }

    async with aiofiles.open(LOG_FILE, mode="a", encoding="utf-8") as f:
        await f.write(json.dumps(log_entry, ensure_ascii=False, indent=2) + "\n")

async def get_db_state(user_id: int) -> dict:
    """
    Собирает состояние пользователя и текущей сказки, включая диалог.

    :param user_id: Идентификатор пользователя
    :return: Словарь с данными пользователя и (если есть) данными текущей сказки
    """
    try:
        # Данные пользователя
        user_data = {
            "age": await get_user_field(user_id, "age"),
            "name": await get_user_field(user_id, "name"),
            "hobby": await get_user_field(user_id, "hobby"),
            "menu": await get_user_field(user_id, "menu"),
            "sex": await get_user_field(user_id, "sex"),
            "cur_tale": await get_user_field(user_id, "cur_tale"),
            "last_message": await get_user_field(user_id, "last_message")
        }

        # Текущая незавершённая сказка (если есть)
        tale_num = await get_tales_num(user_id)
        if not tale_num or tale_num == return_fail_value:
            return {"user": user_data, "tale": None}

        tale_size = await get_tales_field(tale_num, "tale_size")
        if tale_size == return_fail_value or tale_size is None:
            return {"user": user_data, "tale": None}

        answers = await get_parts_tale(tale_num, tale_size)

        tale_data = {
            "tale_num": tale_num,
            "tale_size": tale_size,
            "cur_stage": await get_tales_field(tale_num, "cur_stage"),
            "genre": await get_tales_field(tale_num, "genre"),
            "hero": await get_tales_field(tale_num, "hero"),
            "moral": await get_tales_field(tale_num, "moral"),
            "answer": answers[-1]
        }

        return {"user": user_data, "tale": tale_data}

    except Exception as e:
        print(f"[ERROR] get_db_state: {e}")
        return {"error": str(e)}