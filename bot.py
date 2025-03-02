import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from openai import OpenAI

# Загружаем переменные окружения из .env
load_dotenv()

# Получаем настройки из .env
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID"))  # ID группы
TARGET_THREAD_ID = int(os.getenv("TARGET_THREAD_ID"))  # ID топика

# Настроим логирование
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Подключаемся к DeepSeek API через OpenAI SDK
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

async def get_deepseek_response(user_message: str) -> str:
    """Запрашивает ответ у DeepSeek API (модель deepseek-reasoner)"""
    try:
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": user_message},
            ],

            stream=False
        )
        logging.info(f"Ответ от DeepSeek API: {response}")
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Ошибка при запросе к DeepSeek API: {e}")
        return "Ошибка при получении ответа."

@dp.message()
async def handle_message(message: Message):
    logging.info(f"Получено сообщение от {message.from_user.id}: {message.text}")
    if message.chat.id == TARGET_CHAT_ID and message.message_thread_id == TARGET_THREAD_ID:
        response = await get_deepseek_response(message.text)
        await message.reply(response)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
