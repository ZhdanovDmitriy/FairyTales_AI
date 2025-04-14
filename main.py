import asyncio
from config import bot, dp
from dbtools import fetch_current_db, check_all_users, print_table
from handlers import chat_handler
from callbacks import process_tale, process_settings, process_back

async def main():
    # await fetch_current_db()
    # await check_all_users()
    await print_table("users")
    await print_table("tales")
    await print_table("small_tale")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())