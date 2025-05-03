import asyncio
from config import bot, dp
from dbtools import print_table, reset_all_process_values
from handlers import chat_handler
from callbacks import process_callback
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

async def main():
    try:
        await reset_all_process_values()
        await print_table("users")
        await print_table("tales")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
