import asyncio
import logging
import os  # <-- ДОБАВИТЬ ЭТУ СТРОКУ
from aiogram import Bot, Dispatcher, types

# Теперь бот берёт токен из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")  # токен из Environment Variables на Render

TARGET_TAG = "Режиссёр"

# Проверка: если токен не найден, бот не запустится
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден! Добавьте переменную окружения BOT_TOKEN на Render")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def handle_director_message(message: types.Message):
    if message.sender_tag != TARGET_TAG:
        return
    
    await message.delete()
    
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"🎬 <b>ВНИМАНИЕ! Сообщение от нашего Режиссёра!</b> 🎬\n\n{message.text}",
        parse_mode="HTML"
    )

async def main():
    print("Бот запущен и слушает сообщения...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
