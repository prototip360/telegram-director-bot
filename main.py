import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiohttp import web  # ДОБАВЛЕНА НОВАЯ БИБЛИОТЕКА

BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_TAG = "Режиссёр"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден!")

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
    # Запускаем бота в фоне
    polling_task = asyncio.create_task(dp.start_polling(bot))
    
    # Запускаем веб-сервер для Render Health Check
    app = web.Application()
    
    async def health_check(request):
        return web.Response(text="OK")
    
    app.router.add_get("/healthz", health_check)
    
    # Запускаем веб-сервер на порту 8000
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()
    
    print("Бот запущен и слушает сообщения...")
    print("Веб-сервер для Health Check запущен на порту 8000")
    
    # Ждём завершения работы бота
    await polling_task

if __name__ == "__main__":
    asyncio.run(main())
