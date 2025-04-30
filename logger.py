import aiofiles
from datetime import datetime
import json
from typing import Any
from dbtools import get_user_field

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
        await f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

async def get_db_state(user_id: int):
    user_data = {
        "age": await get_user_field(user_id, "age"),
        "name": await get_user_field(user_id, "name"),
        "hobby": await get_user_field(user_id, "hobby"),
        "menu": await get_user_field(user_id, "menu")
    }
    return user_data