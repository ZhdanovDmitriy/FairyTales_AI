import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("API_KEY")
TEMPERATURE = 1.5
PROMT = (
    "Ты сочинитель сказки для детей. Твоя задача создать сказку из 8-ти частей используя круг Хармона: "
    "обычная жизнь, желание или проблема, новый мир или некомфортная ситуация, адаптация или поиск желаемого, достижение желаемого, "
    "расплата за успех, возвращение, демонстрация изменений. Сказка должна быть понятна ребенку и развивать в нем "
    "правильную моральность. Вначале тебе скажут, кто будет главным героем. Далее ты создашь первую часть сказки "
    "и задашь вопрос, который будет являются отправной точкой для следующего блока сказки. После каждого ответа "
    "задавай вопрос, чтобы на основе его продолжить сказку. Так ты должен пройти все восемь этапов. "
    "У сказки должен быть счастливый финал. Избегай в своей сказке агрессии и насилия. "
    "Не пиши заголовки, пиши только основной сюжет сказки и вопрос для развития сюжета в конце каждой части."
)
START_MESSAGE = "Привет!\nЯ дедушка Сказочник.\nДавай я расскажу тебе сказку,\nкто будет главным героем?"

user_contexts = {}

bot = Bot(token=TOKEN)
dp = Dispatcher()

client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

def get_user_context(user_id: int):
    if user_id not in user_contexts:
        user_contexts[user_id] = [{"role": "assistant", "content": PROMT}]
    return user_contexts[user_id]

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(START_MESSAGE)

@dp.message()
async def chat_handler(message: types.Message):
    user_id = message.from_user.id
    context = get_user_context(user_id)
    context.append({"role": "user", "content": message.text})
    waiting_message = await message.answer("Подождите, придумываю сказку...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=context,
        stream=False,
        temperature=TEMPERATURE,
        parallel_tool_calls = True
    )
    bot_response = response.choices[0].message.content
    context.append({"role": "assistant", "content": bot_response})
    current_datetime = datetime.now()
    print(current_datetime, "   ", user_id, " : ", message.text,"\n")
    await bot.delete_message(chat_id=message.chat.id, message_id=waiting_message.message_id)
    await message.answer(bot_response)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())