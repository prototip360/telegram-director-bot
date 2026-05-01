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
    # Проверяем тег
    if message.sender_tag != TARGET_TAG:
        return

    # Обрабатываем ТОЛЬКО текстовые сообщения от Режиссёра
    if not message.text:
        logger.info("Игнорируем медиа от Режиссёра (для второго бота)")
        return

    logger.info(f"Получен текст от Режиссёра: {message.text[:50]}")

    # Формируем текст ответа
    response_text = f"<b>🎬 ВНИМАНИЕ! Сообщение от нашего Режиссёра! 🎬\n\n{message.text}</b>"

    # Если Режиссёр ответил на какое-то сообщение (текст, фото, видео, опрос — любое)
    if message.reply_to_message:
        # Отправляем ответ на ТО САМОЕ сообщение (на которое ответил Режиссёр)
        await bot.send_message(
            chat_id=message.chat.id,
            text=response_text,
            reply_to_message_id=message.reply_to_message.message_id,
            parse_mode="HTML"
        )
        logger.info(f"Ответ отправлен на сообщение {message.reply_to_message.message_id} (тип: {message.reply_to_message.content_type})")
    else:
        # Если Режиссёр просто написал в чат (без ответа)
        await bot.send_message(
            chat_id=message.chat.id,
            text=response_text,
            parse_mode="HTML"
        )
        logger.info("Сообщение отправлено в чат (без ответа)")

    # Удаляем оригинал сообщения Режиссёра
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
    
    print("✅ Первый бот запущен")
    print("✅ Отвечает на ЛЮБЫЕ сообщения, на которые ответил Режиссёр")
    
    await polling_task

if __name__ == "__main__":
    asyncio.run(main())
