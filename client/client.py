from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, WebAppInfo
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import logging
from create_bot import bot, Admin, Chat  # Убедитесь, что этот модуль имплементирован правильно, и все объекты есть
from database import data_base as db  # Подключение к вашей базе данных
from keaboards import client_kb  # Это ваш собственный модуль клавиатур, убедитесь, что он правильный

from datetime import datetime

router_client = Router()

logging.basicConfig(level=logging.INFO)


class Wait(StatesGroup):
    choosing_help = State()

now = datetime.now()

@router_client.message(Command(commands=['start']))
async def start_help_command(message : types.Message):
    user_id = message.from_user.id
    logging.info(f'User {user_id} started the bot at {now}')
    db.cursor.execute('SELECT COUNT(*) FROM user WHERE id = ?', (user_id, ))
    db.conn.commit()
    
    user_count = db.cursor.fetchone()
    user_count = user_count[0]
    
    if user_count == 0:
        is_bot = message.from_user.is_bot
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        username = message.from_user.username
        language_code = message.from_user.language_code
       
        db.cursor.execute('INSERT INTO user (id, is_bot, first_name, last_name, username, language_code) VALUES (?, ?, ?, ?, ?, ?)', 
        (user_id, is_bot, first_name, last_name, username, language_code, ))
        
        db.conn.commit()
        await bot.send_message(chat_id=user_id, text="Вы успешно прошли регистрацию, вот мои возможности\n\n1) /shop - Магазин нашей продукции\n\n2) /help - Помощь в случае возникновения вопросов", reply_markup=client_kb.kb_vibor_client_start)
    
    if user_count != 0:
        await bot.send_message(chat_id=user_id, text="Вот мои возможности!\n\n1) /shop - Магазин нашей продукции\n\n2) /help - Помощь в случае возникновения вопросов", reply_markup=client_kb.kb_vibor_client_start)
        
@router_client.message(Command(commands=['help']))
async def help_command(message : types.Message):
    user_id = message.from_user.id
    logging.info(f'User {user_id} - {message.from_user.first_name} started the bot at {now}')
    db.cursor.execute('SELECT COUNT(*) FROM user WHERE id = ?', (user_id, ))
    db.conn.commit()
    
    user_count = db.cursor.fetchone()
    user_count = user_count[0]
    
    if user_count == 0:
        is_bot = message.from_user.is_bot
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        username = message.from_user.username
        language_code = message.from_user.language_code
        db.cursor.execute('INSERT INTO user (id, is_bot, first_name, last_name, username, language_code) VALUES (?, ?, ?, ?, ?, ?)', 
        (user_id, is_bot, first_name, last_name, username, language_code, ))
        db.conn.commit()
        await bot.send_message(chat_id=user_id, text="Вы успешно прошли регистрацию\n\nЧем могу помочь?", reply_markup=client_kb.kb_vibor_client_start)
        
    
    if user_count != 0:
        
        # builder = ReplyKeyboardBuilder()
        # builder.add(types.KeyboardButton(text='Чат-поддержки', resize_keyboard=True, input_field_placeholder='Выбирай из преложенных', selective=True))
        await bot.send_message(chat_id=user_id, text="Передите по кнопке в чат поддержки", reply_markup=client_kb.kb_vibor_client_help)

@router_client.message(Command(commands=['shop']))
async def shop_command(message : types.Message):
    user_id = message.from_user.id
    await message.delete()
    
    webAppInfo = types.WebAppInfo(url="https://dx78.ru/bot_lira/")
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Сайт', web_app=webAppInfo))
    
    await bot.send_message(chat_id = user_id, text='Чтобы перейти, нажмите на кнопку', reply_markup=builder.as_markup())

@router_client.message(F.text == 'Чат-поддержки')
async def chat_command(message : types.Message, state: FSMContext):
    await state.set_state(Wait.choosing_help)
    user_id = message.from_user.id
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Выйти', resize_keyboard=True, input_field_placeholder='Выбирай из преложенных', selective=True))
    await bot.send_message(chat_id=user_id, text="Напиши ваш вопрос", reply_markup=builder.as_markup())

@router_client.message(Wait.choosing_help, F.text == 'Выйти')
async def form_help_exit(message : types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.clear()
    await bot.send_message(chat_id=user_id, text="До встречь", reply_markup=client_kb.kb_vibor_client_start)

@router_client.message(Wait.choosing_help)
async def form_help(message : types.Message, state: FSMContext):
    now = datetime.now()
    user_id = message.from_user.id
    user_text = message.text
    user_name = message.from_user.first_name
    user_lastname = message.from_user.last_name
    username = message.from_user.username
    formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    await state.clear()
    
    
    if now.weekday() < 5 and now.time() >= datetime.strptime("18:30", "%H:%M").time():
        await bot.send_message(chat_id=user_id, text="Внимание! В связи с тем, что сейчас не рабочее время, ответ на ваш вопрос будет дан утром следующего дня.")
    else:
        await bot.send_message(chat_id=user_id, text="Мы зафиксировали ваш вопрос, на него ответят в ближайшее время", reply_markup=types.ReplyKeyboardRemove())
    if username == None:
        await bot.forward_message(chat_id=Admin.Leonid, from_chat_id=user_id, message_id=message.message_id)
        await bot.send_message(chat_id=Admin.Leonid, text=f'<b>Чат-поддержка</b>\n\n{user_id} - ID Обротившигося\n\n{user_text} - Вопрос Клиента\n\n{user_name} - Имя клиента\n\n{user_lastname} - 2-ое Имя клиента\n\n{formatted_date_time} Время обращения', parse_mode=ParseMode.HTML)
    else:
        await bot.send_message(chat_id=Admin.Leonid, text=f'<b>Чат-поддержка</b>\n\n{user_id} - ID Обротившигося\n\n{user_text} - Вопрос Клиента\n\n{user_name} - Имя клиента\n\n{user_lastname} - 2-ое Имя клиента\n\n@{username}- ссылка на клиента\n\n{formatted_date_time} Время обращения', parse_mode=ParseMode.HTML)


@router_client.message(F.new_chat_members)
async def welcome_new_member(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Магазин", callback_data="shop")],
        [InlineKeyboardButton(text="Помощь", callback_data="help")]
    ])
    BOT_LINK = 'https://t.me/radiolira_bot'
    for new_member in message.new_chat_members:
        try:
            await bot.send_message(new_member.id, "Добро пожаловать в группу! Если у вас возникнут вопросы, обращайтесь.", reply_markup=keyboard)
        except Exception:
            await bot.send_message(
                chat_id=message.chat.id,
                text=(
                    f"Приветствуем, {new_member.full_name}! Не удалось отправить личное сообщение из-за настроек безопасности.\n"
                    f"Вы можете инициировать личный чат, написав сюда: {BOT_LINK}"
                ), message_thread_id=Chat.id_tem_6
            )

@router_client.callback_query(F.data == 'shop')
async def shop_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.delete()
    
    webAppInfo = types.WebAppInfo(url="https://dx78.ru/bot_lira/")
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Сайт', web_app=webAppInfo))
    
    await bot.send_message(chat_id=user_id, text='Чтобы перейти, нажмите на кнопку', reply_markup=builder.as_markup())
    await callback.answer()

@router_client.callback_query(F.data == 'help')
async def help_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    db.cursor.execute('SELECT COUNT(*) FROM user WHERE id = ?', (user_id, ))
    db.conn.commit()
    
    user_count = db.cursor.fetchone()[0]
    
    if user_count == 0:
        is_bot = callback.from_user.is_bot
        first_name = callback.from_user.first_name
        last_name = callback.from_user.last_name
        username = callback.from_user.username
        language_code = callback.from_user.language_code
        db.cursor.execute('INSERT INTO user (id, is_bot, first_name, last_name, username, language_code) VALUES (?, ?, ?, ?, ?, ?)', 
        (user_id, is_bot, first_name, last_name, username, language_code))
        db.conn.commit()
        await bot.send_message(chat_id=user_id, text="Вы успешно прошли регистрацию\n\nЧем могу помочь?", reply_markup=client_kb.kb_vibor_client_start)
    else:
        await bot.send_message(chat_id=user_id, text="Перейдите по кнопке в чат поддержки", reply_markup=client_kb.kb_vibor_client_help)
    await callback.answer()


# ###############################################################################################
# """
# Временное исполение
# """
# ###############################################################################################

# @router_client.message()
# async def time_send():
#     text = 'Доброго времени суток!\nЯ бот помошник, ко мне всегда можно обратиться. 📟'
#     # await bot.send_message(chat_id= -1001966626424, text=text, reply_to_message_id=Chat.id_tem)
#     keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[ 
#         types.InlineKeyboardButton(text="Перейти к боту", url="https://t.me/radiolira_bot") 
#     ]])
#     await bot.send_message(chat_id= -1001966626424, text=text,reply_markup=keyboard)

# @router_client.message(F.text == 'test')
# async def chat_command(message : types.Message, state: FSMContext):
#     user_info = message
#     user_id = message.from_user.id
#     user_info_2 = message.chat.id
#     print(user_info)
#     print(user_info_2)
#     print(user_id)
