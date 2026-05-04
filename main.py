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

    # Обрабатываем ТОЛЬКО текстовые сообщения
    if not message.text:
        logger.info("Игнорируем медиа (для второго бота)")
        return

    # Определяем ID темы
    thread_id = message.message_thread_id

    # Проверяем, есть ли команда в начале сообщения
    text = message.text
    use_quote = False
    
    # Команды: /c, /цитата, /quote
    if text.startswith("/c ") or text.startswith("/цитата ") or text.startswith("/quote "):
        use_quote = True
        # Убираем команду из текста (оставляем только текст после команды)
        text = text.split(" ", 1)[1]
    
    logger.info(f"Получен текст от Режиссёра: {text[:50]}, цитата: {use_quote}")

    # Оформление: классические дефисы (18 шт)
    if use_quote:
        # С цитатным блоком
        response_text = (
            f"🎬 <b>Сообщение от Режиссёра</b> 🎬\n"
            f"{'─' * 18}\n"
            f"<blockquote>{text}</blockquote>\n"
            f"{'─' * 18}"
        )
    else:
        # Без цитаты, просто текст
        response_text = (
            f"🎬 <b>Сообщение от Режиссёра</b> 🎬\n"
            f"{'─' * 18}\n"
            f"{text}\n"
            f"{'─' * 18}"
        )

    # Отправляем ответ
    if message.reply_to_message:
        await bot.send_message(
            chat_id=message.chat.id,
            text=response_text,
            reply_to_message_id=message.reply_to_message.message_id,
            message_thread_id=thread_id,
            parse_mode="HTML"
        )
        logger.info(f"Ответ отправлен на сообщение {message.reply_to_message.message_id}")
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text=response_text,
            message_thread_id=thread_id,
            parse_mode="HTML"
        )
        logger.info("Сообщение отправлено в чат")

    # Удаляем оригинал
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
    print("✅ /c текст → цитата, текст → без цитаты")
    
    await polling_task

if __name__ == "__main__":
    asyncio.run(main())
