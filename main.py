import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.client.session.aiohttp import AiohttpSession
from openai import AsyncOpenAI

# Загружаем переменные окружения из .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")

# Настройка прокси для обхода блокировки Telegram
# Здесь используются публичные прокси. Если один не работает, попробуй поменять на другой из списка:
PROXY_URL = "socks5://185.221.160.172:1080" 

session = AiohttpSession(proxy=PROXY_URL)
bot = Bot(token=BOT_TOKEN, session=session)
dp = Dispatcher()

# Клиент для нейросети (DeepSeek)
client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=BASE_URL
)

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Привет! Я AI-бот на базе DeepSeek. Напиши мне что-нибудь, и я отвечу.")

@dp.message()
async def all_messages_handler(message: types.Message):
    if not message.text:
        return

    # Показываем, что бот "печатает..."
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Ты полезный и дружелюбный ассистент."},
                {"role": "user", "content": message.text}
            ]
        )
        answer = response.choices[0].message.content
        await message.answer(answer)
    except Exception as e:
        logging.error(f"Ошибка LLM: {e}")
        await message.answer(f"Ошибка: {e}")

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())