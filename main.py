import asyncio
from config import bot, dp
from dbtools import print_table
from handlers import chat_handler
from callbacks import process_callback
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)


async def main():
    await print_table("users")
    await print_table("tales")
    await print_table("tiny_tale")
    await print_table("small_tale")
    await print_table("medium_tale")
    await print_table("large_tale")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
