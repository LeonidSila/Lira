from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, WebAppInfo
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import logging
from create_bot import bot, Admin, Chat
from database import data_base as db
from keaboards import client_kb
from datetime import datetime
from aiogram.types import FSInputFile
import os


router_client = Router()

logging.basicConfig(level=logging.INFO)


class Wait(StatesGroup):
    choosing_help = State()


now = datetime.now()


async def register_user(message):
    """Регистрирует пользователя в базе данных."""
    user_id = message.from_user.id
    is_bot = message.from_user.is_bot
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username
    language_code = message.from_user.language_code
    db.cursor.execute(
        'INSERT INTO user (id, is_bot, first_name, last_name, username, language_code) VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, is_bot, first_name, last_name, username, language_code)
    )
    db.conn.commit()


async def send_welcome_message(chat_id):
    """Отправляет приветственное сообщение пользователю."""
    text = "Вот мои возможности!\n\n1) /shop - Магазин нашей продукции\n\n2) /help - Помощь в случае возникновения вопросов"
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=client_kb.kb_vibor_client_start)


@router_client.message(Command(commands=['start']))
async def start_help_command(message: types.Message):
    user_id = message.from_user.id
    logging.info(f'User {user_id} started the bot at {now}')

    if message.from_user.id in Admin.admin_list:
        webAppInfo = types.WebAppInfo(url="https://dx78.ru/bot_lira/admin_lira/")
        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text='Сайт', web_app=webAppInfo))
        keyboard_markup = builder.as_markup(resize_keyboard=True)
        await bot.send_message(chat_id=user_id, text='Добро пожаловать, Сергей\n\nНажмите на кнопку', reply_markup=keyboard_markup)
        return
    db.cursor.execute('SELECT COUNT(*) FROM user WHERE id = ?', (user_id,))
    db.conn.commit()
    user_count = db.cursor.fetchone()[0]

    if user_count == 0:
        await register_user(message)
        await bot.send_message(
            chat_id=user_id,
            text="Вы успешно прошли регистрацию, вот мои возможности\n\n1) /shop - Магазин нашей продукции\n\n2) /help - Помощь в случае возникновения вопросов",
            reply_markup=client_kb.kb_vibor_client_start
        )
    else:
        await send_welcome_message(user_id)


@router_client.message(Command(commands=['help']))
async def help_command(message: types.Message):
    user_id = message.from_user.id
    logging.info(f'User {user_id} - {message.from_user.first_name} started the bot at {now}')

    if message.from_user.id in Admin.admin_list:
        webAppInfo = types.WebAppInfo(url="https://dx78.ru/bot_lira/admin_lira/")
        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text='Сайт', web_app=webAppInfo))
        keyboard_markup = builder.as_markup(resize_keyboard=True)
        await bot.send_message(chat_id=user_id, text='Добро пожаловать, Сергей\n\nНажмите на кнопку',
                               reply_markup=keyboard_markup)
        return

    db.cursor.execute('SELECT COUNT(*) FROM user WHERE id = ?', (user_id,))
    db.conn.commit()
    user_count = db.cursor.fetchone()[0]

    if user_count == 0:
        await register_user(message)
        await bot.send_message(chat_id=user_id, text="Вы успешно прошли регистрацию\n\nЧем могу помочь?",
                               reply_markup=client_kb.kb_vibor_client_start)
    else:
        await bot.send_message(chat_id=user_id, text="Передите по кнопке в чат поддержки",
                               reply_markup=client_kb.kb_vibor_client_help)


@router_client.message(Command(commands=['shop']))
async def shop_command(message: types.Message):
    user_id = message.from_user.id
    await message.delete()

    webAppInfo = types.WebAppInfo(url="https://dx78.ru/bot_lira/")
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Сайт', web_app=webAppInfo))

    await bot.send_message(chat_id=user_id, text='Чтобы перейти, нажмите на кнопку', reply_markup=builder.as_markup())


@router_client.message(F.text == 'Чат-поддержки')
async def chat_command(message: types.Message, state: FSMContext):
    await state.set_state(Wait.choosing_help)
    user_id = message.from_user.id
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text='Выйти', resize_keyboard=True, input_field_placeholder='Выбирай из преложенных',
                             selective=True))
    await bot.send_message(chat_id=user_id, text="Напиши ваш вопрос", reply_markup=builder.as_markup())


@router_client.message(Wait.choosing_help, F.text == 'Выйти')
async def form_help_exit(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.clear()
    await bot.send_message(chat_id=user_id, text="До встречь", reply_markup=client_kb.kb_vibor_client_start)


async def send_question_to_admin(user_id, user_text, user_name, user_lastname, username, formatted_date_time, message):
    """Отправляет вопрос пользователя администратору."""
    if username is None:
        await bot.forward_message(chat_id=Admin.Leonid, from_chat_id=user_id, message_id=message.message_id)
        await bot.forward_message(chat_id=Admin.Serei, from_chat_id=user_id, message_id=message.message_id)
        await bot.send_message(chat_id=Admin.Leonid,
                               text=f'<b>Чат-поддержка</b>\n\n{user_id} - ID Обротившигося\n\n{user_text} - Вопрос Клиента\n\n{user_name} - Имя клиента\n\n{user_lastname} - 2-ое Имя клиента\n\n{formatted_date_time} Время обращения',
                               parse_mode=ParseMode.HTML)
        await bot.send_message(chat_id=Admin.Serei,
                               text=f'<b>Чат-поддержка</b>\n\n{user_id} - ID Обротившигося\n\n{user_text} - Вопрос Клиента\n\n{user_name} - Имя клиента\n\n{user_lastname} - 2-ое Имя клиента\n\n{formatted_date_time} Время обращения',
                               parse_mode=ParseMode.HTML)
    else:
        await bot.send_message(chat_id=Admin.Leonid,
                               text=f'<b>Чат-поддержка</b>\n\n{user_id} - ID Обротившигося\n\n{user_text} - Вопрос Клиента\n\n{user_name} - Имя клиента\n\n{user_lastname} - 2-ое Имя клиента\n\n@{username}- ссылка на клиента\n\n{formatted_date_time} Время обращения',
                               parse_mode=ParseMode.HTML)
        await bot.send_message(chat_id=Admin.Serei,
                               text=f'<b>Чат-поддержка</b>\n\n{user_id} - ID Обротившигося\n\n{user_text} - Вопрос Клиента\n\n{user_name} - Имя клиента\n\n{user_lastname} - 2-ое Имя клиента\n\n{formatted_date_time} Время обращения',
                               parse_mode=ParseMode.HTML)

@router_client.message(Wait.choosing_help)
async def form_help(message: types.Message, state: FSMContext):
    now = datetime.now()
    user_id = message.from_user.id
    user_text = message.text
    user_name = message.from_user.first_name
    user_lastname = message.from_user.last_name
    username = message.from_user.username
    formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    await state.clear()

    if now.weekday() < 5 and now.time() >= datetime.strptime("18:30", "%H:%M").time():
        await bot.send_message(chat_id=user_id,
                               text="Внимание! В связи с тем, что сейчас не рабочее время, ответ на ваш вопрос будет дан утром следующего дня.")
    else:
        await bot.send_message(chat_id=user_id, text="Мы зафиксировали ваш вопрос, на него ответят в ближайшее время",
                               reply_markup=types.ReplyKeyboardRemove())

    await send_question_to_admin(user_id, user_text, user_name, user_lastname, username, formatted_date_time, message)


@router_client.message(F.new_chat_members)
async def welcome_new_member(message: Message):
    text = (
        "👋 Приветствуем вас в группе от лица компании «Радиосвязь СПб»!\n\n"
        "Администратор канала - Сергей - @DX78RU\n\n"
        "Для получения оперативной информации инициализируетесь в чате с ботом\n"
        "📍 Наш адрес:\n"
        "Чугунная ул., дом 40, Офис 416, Санкт-Петербург, 195044\n\n"
        "📞 Связаться с нами можно:\n"
        " • по телефону: +7 (921) 935-24-92\n"
        " • по почте: cb78@mail.ru\n"
        " • а также прямо здесь, в чате с ботом!\n\n"
        "🤓 Задайте интересующий вас вопрос, и мы с радостью вас проконсультируем."
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Магазин", callback_data="shop")],
        [InlineKeyboardButton(text="Помощь", callback_data="help")]
    ])
    BOT_LINK = 'https://t.me/radiolira_bot'
    for new_member in message.new_chat_members:
        try:
            photo = FSInputFile('photo/logo.png')
            await bot.send_photo(
                chat_id=new_member.id,
                photo=photo,
                caption=text,
            )
            await bot.send_location(
                chat_id=new_member.id,
                latitude=59.970992,  # Замените на фактические координаты
                longitude=30.364126,  # Замените на фактические координаты
            )
    
            await bot.send_message(new_member.id, "Добро пожаловать в группу! Если у вас возникнут вопросы, обращайтесь.",
                                   reply_markup=keyboard)
        except Exception:    
            await bot.send_message(
                chat_id=Admin.Serei,
                text=(
                    f"Cергей! Появился новый пользователь {new_member.full_name} в группе, и мне не удалось отправить сообщение."))
            await bot.send_message(
                chat_id=Admin.Leonid,
                text=(
                    f"Cергей! Появился новый пользователь {new_member.full_name} в группе, и мне не удалось отправить сообщение."))


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

    db.cursor.execute('SELECT COUNT(*) FROM user WHERE id = ?', (user_id,))
    db.conn.commit()
    user_count = db.cursor.fetchone()[0]

    if user_count == 0:
        register_user(callback.from_user)
        await bot.send_message(chat_id=user_id, text="Вы успешно прошли регистрацию\n\nЧем могу помочь?",
                               reply_markup=client_kb.kb_vibor_client_start)
    else:
        await bot.send_message(chat_id=user_id, text="Перейдите по кнопке в чат поддержки",
                               reply_markup=client_kb.kb_vibor_client_help)
    await callback.answer()

@router_client.message(Command(commands=['info']))
async def send_info(message: types.Message):
    user_id = message.from_user.id
    """Отправляет информацию о компании "Радиосвязь СПб"."""

    text = (
        "👋 Приветствуем вас в группе от лица компании «Радиосвязь СПб»!\n\n"
        "Администратор канала - Сергей - @DX78RU\n\n"
        "Для получения оперативной информации инициализируетесь в чате с ботом\n"
        "📍 Наш адрес:\n"
        "Чугунная ул., дом 40, Офис 416, Санкт-Петербург, 195044\n\n"
        "📞 Связаться с нами можно:\n"
        " • по телефону: +7 (921) 935-24-92\n"
        " • по почте: cb78@mail.ru\n"
        " • а также прямо через чат с ботом!\n\n"
        "🤓 Задайте интересующий вас вопрос, и мы с радостью вас проконсультируем."
    )

    # Отправка сообщения с фото, текстом и картой
    try:
        photo = FSInputFile('photo/logo.png')
        await bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption=text,
        )
    except Exception as e:
        print(f"Ошибка: {e}")
    await bot.send_location(
        chat_id=user_id,
        latitude=59.970992,  # Замените на фактические координаты
        longitude=30.364126,  # Замените на фактические координаты
    )
    
