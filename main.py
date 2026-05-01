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
    # Проверяем тег отправителя
    if message.sender_tag != TARGET_TAG:
        return

    logger.info(f"Получено сообщение типа: {message.content_type}")

    # Удаляем оригинал
    try:
        await message.delete()
        logger.info("Оригинал удалён")
    except Exception as e:
        logger.warning(f"Не удалось удалить оригинал: {e}")

    # Отправляем ответ в зависимости от типа
    try:
        if message.text:
            # Текстовое сообщение → полужирный стиль
            await bot.send_message(
                chat_id=message.chat.id,
                text=f"<b>🎬 ВНИМАНИЕ! Сообщение от нашего Режиссёра! 🎬\n\n{message.text}</b>",
                parse_mode="HTML"
            )
            logger.info("Текст отправлен")
        else:
            # Медиа (фото, видео, файлы, опросы) → копируем как есть
            await bot.copy_message(
                chat_id=message.chat.id,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            logger.info(f"Медиа скопировано: {message.content_type}")
    except Exception as e:
        logger.error(f"Ошибка при отправке: {e}")

async def main():
    # Запускаем бота (long polling)
    polling_task = asyncio.create_task(dp.start_polling(bot))
    
    # Запускаем веб-сервер для Health Check (на случай, если перейдёте на Webhook)
    app = web.Application()
    
    async def health_check(request):
        return web.Response(text="OK")
    
    app.router.add_get("/healthz", health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()
    
    print("✅ Бот запущен и слушает сообщения...")
    print("✅ Поддерживает текст (полужирный), фото, видео, файлы, опросы")
    print("✅ Веб-сервер для Health Check на порту 8000")
    
    await polling_task

if __name__ == "__main__":
    asyncio.run(main())
