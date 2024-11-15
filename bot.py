import asyncio
import logging
from client import client as cl
from saint import client_sait as sc
from database import data_base
from create_bot import dp, bot, Chat
from admin import admin
from aiogram.methods import DeleteWebhook
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import types


# Инициализация базы данных
data_base.creat_teble()

# Подключение маршрутизаторов
dp.include_router(cl.router_client)
dp.include_router(sc.router_client_sait)
dp.include_router(admin.router_admin)

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# # Инициализация планировщика
# scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
# scheduler.add_job(cl.time_send, trigger='cron', hour=2, minute=1, kwargs={'bot': bot})
# scheduler.start()

# async def time_send():
#     """
#     Отправляет приветственное сообщение в чат с кнопкой ссылки на бот.
#     """
#     text = 'Доброго времени суток!\nЯ бот помощник, ко мне всегда можно обратиться. 📟'
#     keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
#         [types.InlineKeyboardButton(text="Перейти к боту", url="https://t.me/radiolira_bot")]
#     ])
#     await bot.send_message(chat_id=Chat.chat_id, text=text, reply_markup=keyboard)

async def start():
    try:
        await dp.start_polling(bot)
        await bot(DeleteWebhook(drop_pending_updates=True))
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())