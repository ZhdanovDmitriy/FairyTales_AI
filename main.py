import asyncio
from config import bot, dp
from dbtools import print_table
from handlers import chat_handler
from callbacks import process_callback

async def main():
    await print_table("users")
    await print_table("tales")
    await print_table("small_tale")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())    