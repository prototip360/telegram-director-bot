import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_TAG = "Режиссёр"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден!")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def handle_director_message(message: types.Message):
    if message.sender_tag != TARGET_TAG:
        return

    if not message.text:
        logger.info("Игнорируем медиа (для второго бота)")
        return

    logger.info(f"Получен текст от Режиссёра: {message.text[:50]}")

    response_text = f"<b>🎬 ВНИМАНИЕ! Сообщение от нашего Режиссёра! 🎬\n\n{message.text}</b>"

    # Определяем ID темы (если сообщение из темы)
    thread_id = message.message_thread_id  # будет None, если темы нет

    # Если Режиссёр ответил на чьё-то сообщение
    if message.reply_to_message:
        await bot.send_message(
            chat_id=message.chat.id,
            text=response_text,
            reply_to_message_id=message.reply_to_message.message_id,
            message_thread_id=thread_id,  # КЛЮЧЕВОЙ ПАРАМЕТР
            parse_mode="HTML"
        )
        logger.info(f"Ответ отправлен в тему {thread_id or 'основную'}")
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text=response_text,
            message_thread_id=thread_id,  # КЛЮЧЕВОЙ ПАРАМЕТР
            parse_mode="HTML"
        )
        logger.info(f"Сообщение отправлено в тему {thread_id or 'основную'}")

    await message.delete()
    logger.info("Оригинал удалён")

async def main():
    polling_task = asyncio.create_task(dp.start_polling(bot))
    
    app = web.Application()
    
    async def health_check(request):
        return web.Response(text="OK")
    
    app.router.add_get("/healthz", health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()
    
    print("✅ Первый бот запущен с поддержкой тем")
    
    await polling_task

if __name__ == "__main__":
    asyncio.run(main())
