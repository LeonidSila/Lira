from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from create_bot import dp, bot
from aiogram.utils.keyboard import ReplyKeyboardBuilder

kb_vibor_client_start = ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text = '/shop'), 
         types.KeyboardButton(text = '/help')],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Чего ты хочешь?',
    selective=True

)

kb_vibor_client_help = ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text = 'Чат-поддержки')],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Чего ты хочешь?',
    selective=True

)