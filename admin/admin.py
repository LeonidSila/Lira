from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from create_bot import bot, Admin, Chat
from database import data_base as db
from keaboards import admin_kb
from fuzzywuzzy import process

import sqlite3

router_admin = Router()

class WaitAdmin(StatesGroup):
    admin_wait = State()
    admin_wait_2 = State()
    admin_wait_3 = State()
    waiting_for_caption = State()
    admin_wait_media = State()
    admin_wait_f2 = State()
#@router_admin.message()
#async def shop_command_admin(message: types.Message):
#    print(message)

@router_admin.message(Command(commands=['admin']))
async def admin_command(message: types.Message):
    user_id = message.from_user.id
    user_text = message.text
    user_name = message.from_user.first_name
    user_lastname = message.from_user.last_name
    username = message.from_user.username

    await bot.forward_message(chat_id=Admin.Leonid, from_chat_id=user_id, message_id=message.message_id)

    if user_id not in Admin.admin_list:
        log_message = (
            f"Была попытка зайти под админ учеткой\n"
            f"ID: {user_id}\n"
            f"Текст: {user_text}\n"
            f"Имя: {user_name}\n"
            f"Фамилия: {user_lastname}\n"
            f"Username: {username}"
        )
        await bot.send_message(chat_id=Admin.Leonid, text=log_message)
        await bot.send_message(chat_id=user_id, text='Таких админов нет')
    else:
        await bot.send_message(chat_id=user_id, text="Добро пожаловать!\n\nНа данный момент доступны следующие функции", reply_markup=admin_kb.kb_vibor_admin)

@router_admin.message(F.text == '4: Выйти')
async def exit_command(message: types.Message):
    user_id = message.from_user.id
    await bot.send_message(chat_id=user_id, text="Будем ждать", reply_markup=types.ReplyKeyboardRemove())

@router_admin.message(F.text == '3: Магазин')
async def shop_command_admin(message: types.Message):
    user_id = message.from_user.id

    web_app_info = types.WebAppInfo(url="https://rabotanadsaitom.space/bot_lira/")
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(types.KeyboardButton(text='Сайт', web_app=web_app_info))

    await bot.send_message(chat_id=user_id, text='Перейдите по ссылке', reply_markup=keyboard.as_markup())
######################################################################################################
@router_admin.message(F.text =='1: Рассылка, через бота')
async def broadcast_command(message: types.Message, state: FSMContext):
    await state.set_state(WaitAdmin.admin_wait)
    user_id = message.from_user.id
    await bot.send_message(
        chat_id=user_id,
        text="Сообщение для рассылки. Вы можете отправить текст, фото, видео или документ.",
        reply_markup=types.ReplyKeyboardRemove()
    )

@router_admin.message(F.text =='7: Чистка базы от мусора если есть')
async def admin_clier_db(message: types.Message, state: FSMContext):
    def remove_duplicate_ids():
        """
        Удаляет дубликаты значений в столбце 'id' таблицы 'user' в базе данных.

        Args:
            db_path: Путь к файлу базы данных (например, 'mydatabase.db').
        
        Returns:
            None. Выводит сообщение об успехе или ошибке.  
            Возвращает количество удаленных строк.
        """
        try:
            # Сначала получаем список всех уникальных id
            db.cursor.execute("SELECT DISTINCT id FROM user")
            unique_ids = [row[0] for row in db.cursor.fetchall()]
            
            #  Важно:  Удалить повторяющиеся id, не изменяя порядок.
            #  Не используем DELETE FROM ... WHERE id IN (SELECT id FROM user GROUP BY id HAVING COUNT(*) > 1)

            count_deleted = 0
            for id_val in unique_ids:
                db.cursor.execute(
                    """
                    DELETE FROM user
                    WHERE id = ?
                    AND ROWID NOT IN (SELECT MIN(ROWID) FROM user WHERE id = ?)
                    """, (id_val, id_val)
                )
                count_deleted += db.cursor.rowcount  # Считаем удаленные строки

            db.conn.commit()
            print(f"Удалено {count_deleted} дубликатов в таблице 'user'.")
            db.conn.close()
            return count_deleted

        except sqlite3.Error as e:
            print(f"Ошибка при работе с базой данных: {e}")
            return None  # Указываем, что произошла ошибка

        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")
            return None
    result = remove_duplicate_ids()

    if result is not None:
        print(f"Функция выполнена успешно. Удалено {result} записей.")
        await bot.send_message(chat_id=message.from_user.id, text=f"Функция выполнена успешно. Удалено {result} записей.")


@router_admin.message(WaitAdmin.admin_wait)
async def broadcast_message(message: types.Message, state: FSMContext):
    if message.content_type == types.ContentType.TEXT:
        await send_to_all_users(message.text)
        await state.clear()
        await bot.send_message(chat_id=message.from_user.id, text='Рассылка завершена', reply_markup=types.ReplyKeyboardRemove())
    elif message.content_type in [types.ContentType.PHOTO, types.ContentType.VIDEO, types.ContentType.DOCUMENT]:
        await state.update_data(media=message)
        await state.set_state(WaitAdmin.admin_wait_media)
        await bot.send_message(
            chat_id=message.from_user.id,
            text="Введите текст, который будет прикреплен к медиафайлу."
        )
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="Этот тип сообщения не поддерживается для рассылки."
        )

@router_admin.message(WaitAdmin.admin_wait_media)
async def receive_media_caption(message: types.Message, state: FSMContext):
    data = await state.get_data()
    media = data.get('media')
    
    await process_and_send_media(media, message.text)
    await state.clear()
    await bot.send_message(chat_id=message.from_user.id, text='Рассылка завершена', reply_markup=types.ReplyKeyboardRemove())

async def send_to_all_users(text):
    try:
        db.cursor.execute('SELECT id FROM user')
        db.conn.commit()
        user_ids = db.cursor.fetchall()

        for user in user_ids:
            await bot.send_message(chat_id=user[0], text=text)
    except Exception as e:
        await bot.send_message(chat_id=Admin.Leonid, text=f"Ошибка при отправке сообщения: {e}")

async def process_and_send_media(message, caption):
    try:
        db.cursor.execute('SELECT id FROM user')
        db.conn.commit()
        user_ids = db.cursor.fetchall()

        for user in user_ids:
            if message.content_type == types.ContentType.PHOTO:
                await bot.send_photo(chat_id=user[0], photo=message.photo[-1].file_id, caption=caption)
            elif message.content_type == types.ContentType.VIDEO:
                await bot.send_video(chat_id=user[0], video=message.video.file_id, caption=caption)
            elif message.content_type == types.ContentType.DOCUMENT:
                await bot.send_document(chat_id=user[0], document=message.document.file_id, caption=caption)
    except Exception as e:
        await bot.send_message(chat_id=Admin.Leonid, text=f"Ошибка при отправке сообщения: {e}")
######################################################################################################################################
# Идентификаторы чатов
# chat_ids = {
#     "test1": 2138,
#     "test2": 1916,
#     "test3": 2153,
#     "test4": 2143,
#     "test5": 2145,
#     "test6": 2147,
#     "test7": 2149
# } #ТЕСТ
chat_ids = {
    "Срочные сообщения": 11473,
    "Полезные ссылки": 3925,
    "Месенджеры": 12649,
    "Софт по другим радиостанциям": 715,
    "ВЕДА": 11135,
    "Гарантия Оборудование": 6279,
    "Ретрансляторы ДМР Lira": 4927,
    "Lira. Софт. Рекомендации . Обсуждения": 702,
    "Дремучая дичь в установке антенн": 11423,
    "Заказ раций, обмен, продажа": 6332,
    "Ветерок Артгруппа": 11502,
    "Организация связи. Настройки": 732,
    "ZOV карты": 9504,
    "Детекторы дронов. Оптимизация выбора": 10436,
    "Антенны. Литература и информация": 8516,
    "Глушилки. Дронов, связи и тд": 1655,
    "Соседи": 7791,
    "Анонс нового оборудования": 11674,
    "Дроны": 745,
    "ГРОЗА Программа корректировки огня": 6318,
    "Решение для установки в технику": 3623,
    "Софт Lira. Примеры прошивок": 3412,
    "Дронница 2024": 15967,
    "Не рэб средство индивидуальной защиты": 15710,
    "Все по антеннам укв": 719,
    "КЦПН Координационный Центр помощи": 11814,
    "Артиллерия вопросы. Помощь профессионалов": 2723,
    "Asel детектор дронов": 14961,
    "NANO VNA": 7445,
    "Борьба с FPV": 11302,
    "KillCode": 5019,
    "Памяти": 10200,
    "Тактическая медицина": 12990,
    "Радиомониторинг": 720,
    "Крипта": 1071,
    "Авиационная связь. И возможное взаимодействие": 934,
    "ГПС Навигация. Полезный софт": 743,
    "Вопросы в Академию связи": 11298,
    "Предложения ВУЗов по нашей тематике": 11812,
    "Репей Созвездие": 7901,
    "Для добавления связистов и причастных, пишите": 10021,
    "Сторонние ПО потРСТ": 5465,
    "Новости в связи от противника": 8546,
    "Полезная литература для связистов": 8511,
    "Пожелания и негатив по Lira": 718,
    "Сотник": 7214,
    "При проблемах с РСТ. Гарантия": 1397,
    "Маскировка объектов. Техники. Ложные": 2273,
    "Периферия для раций. Обсуждение только": 3840,
    "Обсуждение установок радиостанций": 835,
    "Информация по наличию оборудования": 1838,
    "Помехи связи противнику": 2685
}


available_topic_names = ',  '.join(chat_ids.keys())

@router_admin.message(F.text == '5: Рассылка, в чат')
async def chat_broadcast_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.set_state(WaitAdmin.admin_wait_2)
    prompt_text = (
        f"Доступные темы: \n\n{available_topic_names}\n\n"
        "Введите темы для рассылки, через запятые (формат ввода может быть произвольным):"
    )
    await bot.send_message(chat_id=user_id, text=prompt_text)

@router_admin.message(WaitAdmin.admin_wait_2)
async def choose_topics(message: types.Message, state: FSMContext):
    user_text = message.text
    entered_topics = user_text.split(',')
    matched_topics = []

    for topic in entered_topics:
        topic = topic.strip()
        if not topic:
            continue

        best_match = process.extractOne(topic, chat_ids.keys(), score_cutoff=60)
        if best_match:
            matched_topics.append(chat_ids[best_match[0]])

    if not matched_topics:
        available_topics_list = ',  '.join(chat_ids.keys())
        await message.answer(f"Темы не найдены. Доступные темы: \n\n{available_topics_list}\n\n")
    else:
        # Сохраняем информацию о выбранных темах в состояние
        await state.update_data(selected_topics=matched_topics)
        await state.set_state(WaitAdmin.admin_wait_3)
        await message.answer("Темы выбраны. Пожалуйста, введите текст сообщения или прикрепите файл.")

@router_admin.message(WaitAdmin.admin_wait_3)
async def gather_and_send_message(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    matched_topics = state_data.get('selected_topics', [])

    if not matched_topics:
        await message.answer("Невозможно отправить сообщение: темы не были выбраны ранее.")
    else:
        # Сохраняем файл, если он есть, и текущее состояние с matched_topics
        if message.photo or message.document:
            await state.update_data(media=message.photo[-1].file_id if message.photo else message.document.file_id)
            await state.update_data(matched_topics=matched_topics)
            await message.answer("Введите текст, который будет отправлен с фото или документом. Если ничего вводить не нужно, просто отправьте пустое сообщение.")
            await state.set_state(WaitAdmin.waiting_for_caption)
        else:
            await send_message_to_topics(message.text or "", matched_topics)
            await state.clear()

@router_admin.message(WaitAdmin.waiting_for_caption)
async def receive_caption(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    text = message.text or ""
    media_id = state_data.get('media')
    matched_topics = state_data.get('matched_topics', [])

    if media_id:
        for topic_id in matched_topics:
            try:
                if message.photo:
                   await bot.send_photo(chat_id=Chat.chat_id, photo=media_id, caption=text, message_thread_id=topic_id)
                elif message.document:
                   await bot.send_document(chat_id=Chat.chat_id, document=media_id, caption=text, message_thread_id=topic_id)
                else:
                   await bot.send_message(chat_id=Chat.chat_id, text=text, message_thread_id=topic_id)
                await bot.send_message(chat_id=message.from_user.id, text=f"Рассылка отправлена в тему {topic_id}")
            except Exception as e:
                error_message = f"Ошибка при отправке сообщения в тему {topic_id}: {e}"
                print(error_message)
                await bot.send_message(chat_id=Admin.Leonid, text=error_message)

    await state.clear()

async def send_message_to_topics(text, matched_topics):
    for topic_id in matched_topics:
        try:
            await bot.send_message(chat_id=Chat.chat_id, text=text, message_thread_id=topic_id)
        except Exception as e:
            error_message = f"Ошибка при отправке сообщения в тему {topic_id}: {e}"
            print(error_message)
            await bot.send_message(chat_id=Admin.Leonid, text=error_message)

######################################################################################################################################
@router_admin.message(WaitAdmin.admin_wait_2)
async def chat_broadcast_text(message: types.Message, state: FSMContext):
    user_text = message.text
    chat_ids = [Chat.id_tem_1, Chat.id_tem_2, Chat.id_tem_3] # Основа
    #chat_ids = [Chat.id_tem, Chat.id_tem1] # Для тестов
    #await bot.send_message(chat_id=Chat.chat_id, text=user_text)
    try: 
        for i in range(len(chat_ids)):
            await bot.send_message(chat_id=Chat.chat_id, text=user_text, message_thread_id=chat_ids[i])
    except Exception as e:
        print(f"Error sending message to {chat_ids[i]}: {e}")
        #await bot.send_message(chat_id = Admin.Leonid, text= e)
    #await bot.send_message(chat_id=Chat.chat_id, text=user_text, message_thread_id=Chat.id_tem_1)

    await state.clear()

@router_admin.message(F.text == '2: Кол-во в базе')
async def user_count_command(message: types.Message):
    user_id = message.from_user.id
    db.cursor.execute('SELECT COUNT(*) FROM user')
    db.conn.commit()
    user_count = db.cursor.fetchone()[0]
    
    await bot.send_message(chat_id=user_id, text=f'{user_count} - Количество пользователей')

@router_admin.message(F.text == '6: import_users')
async def import_users(message: types.Message):
    if message.from_user.id not in Admin.admin_list:
        await message.reply("У вас нет прав для выполнения этой команды.")
        return

    try:
        members = await bot.get_chat_administrators(Chat.chat_id)
        for member in members:
            print(f"Processing user ID: {member.user.id}")
        for member in members:
            user_id = member.user.id
            is_bot = member.user.is_bot
            first_name = member.user.first_name or ''
            last_name = member.user.last_name or ''
            username = member.user.username or ''
            language_code = member.user.language_code or ''

            # Проверка наличия пользователя в базе данных
            db.cursor.execute('SELECT 1 FROM test WHERE id = ?', (user_id,))
            exists = db.cursor.fetchone()
            
            if not exists:
                # Занести данные в базу данных
                db.cursor.execute(
                    '''INSERT INTO user (id, is_bot, first_name, last_name, username, language_code) 
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (user_id, is_bot, first_name, last_name, username, language_code)
                )
        db.conn.commit()

        await message.reply("Участники успешно добавлены в базу данных.")
    except Exception as e:
        await message.reply(f"Произошла ошибка: {str(e)}")
