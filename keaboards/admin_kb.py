from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from create_bot import dp, bot
from aiogram.utils.keyboard import ReplyKeyboardBuilder

kb_vibor_admin = ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text = '1: Рассылка, через бота'), 
         types.KeyboardButton(text = '2: Кол-во в базе'), 
         types.KeyboardButton(text = '3: Магазин'), 
         types.KeyboardButton(text = '4: Выйти')],
         [types.KeyboardButton(text = '5: Рассылка, в чат')],
         [types.KeyboardButton(text = '6: import_users')]
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder='Чего ты хочешь?',
    selective=True

)

kb_vibor_client_start = ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text = 'Админка')],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Админка, просто нажми на кнопку',
    selective=True

)

