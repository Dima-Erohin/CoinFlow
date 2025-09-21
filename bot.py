from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import asyncio
import os
import db  # твоя логика работы с БД

from dotenv import load_dotenv

# загружаем переменные окружения
load_dotenv()

# теперь переменная BOT_TOKEN доступна
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command(commands=["start"]))
async def start_cmd(message: Message):
    user = {
        "id": message.from_user.id,
        "username": message.from_user.username,
        "phone": message.contact.phone_number if message.contact else None
    }
    await db.add_user_if_not_exists(user)
    await message.answer(text="Привет! Перейди в веб-приложение, чтобы продолжить.")

async def start_bot():
    await dp.start_polling()
