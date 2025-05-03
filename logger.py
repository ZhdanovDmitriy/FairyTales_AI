import aiofiles
from datetime import datetime, timedelta
import json
import os
from typing import Any
from dbtools import (get_user_field, get_tales_num, return_fail_value,get_tales_field, get_parts_tale)

LOG_FOLDER = "logs"

async def log_event(user_id: int, message: str, reaction: str, db_diff: Any = None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_filename = f"{datetime.now().strftime('%Y-%m-%d')}.log"
    log_path = os.path.join(LOG_FOLDER, log_filename)

    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    log_entry = {
        "time": timestamp,
        "user_id": user_id,
        "message": message,
        "reaction": reaction,
        "db_changes": db_diff
    }

    async with aiofiles.open(log_path, mode="a", encoding="utf-8") as f:
        await f.write(json.dumps(log_entry, ensure_ascii=False, indent=2) + "\n")

    await cleanup_old_logs()

async def cleanup_old_logs():
    # Если папки нет — нечего чистить
    if not os.path.isdir(LOG_FOLDER):
        return

    now = datetime.now()
    cutoff = now - timedelta(days=7)

    for filename in os.listdir(LOG_FOLDER):
        if not filename.endswith(".log"):
            continue
        file_date_str = filename[:-4]  #убираем '.log'
        try:
            file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
        except ValueError:
            continue

        if file_date < cutoff:
            try:
                os.remove(os.path.join(LOG_FOLDER, filename))
            except OSError:
                pass

async def get_db_state(user_id: int) -> dict:
    """
    Собирает состояние пользователя и текущей сказки, включая диалог.

    :param user_id: Идентификатор пользователя
    :return: Словарь с данными пользователя и (если есть) данными текущей сказки
    """
    try:
        user_data = {
            "age": await get_user_field(user_id, "age"),
            "name": await get_user_field(user_id, "name"),
            "hobby": await get_user_field(user_id, "hobby"),
            "menu": await get_user_field(user_id, "menu"),
            "sex": await get_user_field(user_id, "sex"),
            "cur_tale": await get_user_field(user_id, "cur_tale"),
            "last_message": await get_user_field(user_id, "last_message"),
            "process": await get_user_field(user_id, "process")
        }

        tale_num = await get_tales_num(user_id)
        if not tale_num or tale_num == return_fail_value:
            return {"user": user_data, "tale": None}

        tale_size = await get_tales_field(tale_num, "tale_size")
        if tale_size in (None, return_fail_value):
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
