import json

from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.enums.content_type import ContentType
from aiogram.enums.parse_mode import ParseMode
from database import data_base as db
from datetime import datetime
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import asyncio
from create_bot import dp, bot, Admin, Chat
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

router_client_sait = Router()
# Словарь для хранения данных о товарах

# Идентификаторы чатов
chat_ids = {
    "test1": 2138,
    "test2": 1916,
    "test3": 2153,
    "test4": 2143,
    "test5": 2145,
    "test6": 2147,
    "test7": 2149
} #ТЕСТ

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

chat_ids_value = [str(value) for value in chat_ids.values()]
# print(chat_ids_value, type(chat_ids_value), 'токины тем')

products = {
    "Рассылка через чат": {
        "title": "Рассылка через чат",
        "desc": "Отправляет сообщение по выбранным темам в основной чат"
    },
    "Рассылка без выбора тем": {
        "title": "Рассылка без выбора тем",
        "desc": "Позволяет отправить сообщение в основной чат без выбора конкретных тем."
    },
}
now = datetime.now()

class Form(StatesGroup):
    waiting_for_confirmation = State()

@router_client_sait.message(F.content_type == ContentType.WEB_APP_DATA)
async def parse_data(message: types.Message, state: FSMContext):
    web_app_data = json.loads(message.web_app_data.data)

    # Функция для создания клавиатуры с кнопками "Да" и "Нет"
    def get_confirmation_keyboard():
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data="confirm:yes")],
            [InlineKeyboardButton(text="Нет", callback_data="confirm:no")]
        ])
        return keyboard

    # Запрос на подтверждение у администратора
    async def request_admin_confirmation(confirmation_message):
        await bot.send_message(chat_id=Admin.Leonid, text=confirmation_message, reply_markup=get_confirmation_keyboard())
        await state.set_state(Form.waiting_for_confirmation)

    if 'themes' in web_app_data and 'message' in web_app_data and len(web_app_data) == 2:
        matched_topics = web_app_data['themes']
        text_user = str(web_app_data['message'])
        confirmation_message = f"Подтвердите отправку сообщения:\nТемы: {matched_topics}\nСообщение: {text_user}"
        await request_admin_confirmation(confirmation_message)

        # Сохраняем данные для использования в обработчике подтверждения
        await state.update_data(matched_topics=matched_topics, text_user=text_user)

    elif 'message' in web_app_data and len(web_app_data) == 1:
        message_user = web_app_data['message']
        confirmation_message = f"Подтвердите отправку сообщения:\nСообщение: {message_user}"
        await request_admin_confirmation(confirmation_message)

        # Сохраняем сообщение для отправки после подтверждения
        await state.update_data(message_to_send=message_user)

    elif len(web_app_data) >= 3 and ('customerName' in web_app_data or 'product' in web_app_data):
        # Товары с сайта
        customer_name = web_app_data['customerName']
        additional_services = web_app_data['additionalServices']
        contactinfo = web_app_data['contactInfo']
        product_title = web_app_data['product']['title']

        formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        result = customer_name, additional_services, contactinfo, product_title

        await bot.send_message(chat_id=Admin.Leonid, text=f'Имя - <b>{result[0]}</b>\n\nДоп Услуга - <b>{result[1]}</b>\n\nКонтакты - <code>{result[2]}\n\nПродукт по которому обратились - <b>{result[3]}</b>\n\nДата- <b>{formatted_date_time}</b>',
                               parse_mode=ParseMode.HTML, reply_markup=types.ReplyKeyboardRemove())
    else:
        await bot.send_message(chat_id=Admin.Leonid, text="Получил данные с сайта, но не смог обработать")

@router_client_sait.callback_query(lambda c: c.data.startswith("confirm:"))
async def process_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    action = callback_query.data.split(":")[1]
    states_data = await state.get_data()  # Получаем состояние

    if action == "yes":
        await state.update_data(confirmation_received=True)  # Обновляем состояние с подтверждением
        matched_topics = states_data.get('matched_topics')
        text_user = states_data.get('text_user')

        if matched_topics:
            for topic_id in matched_topics:
                try:
                    await bot.send_message(chat_id=Chat.chat_id, text=text_user, message_thread_id=topic_id)
                except Exception as e:
                    error_message = f"Ошибка при отправке сообщения в тему {topic_id}: {e}"
                    print(error_message)
                    await bot.send_message(chat_id=Admin.Leonid, text=error_message)

        message_user = states_data.get('message_to_send')
        if message_user:
            try:
                db.cursor.execute('SELECT id FROM user')
                db.conn.commit()
                user_ids = db.cursor.fetchall()
                for user in user_ids:
                    await bot.send_message(chat_id=user[0], text=message_user)
            except Exception as e:
                await bot.send_message(chat_id=Admin.Leonid, text=f"Ошибка при отправке сообщения: {e}")

        await bot.send_message(callback_query.from_user.id, "Сообщение подтверждено и будет отправлено.")
    elif action == "no":
        await bot.send_message(callback_query.from_user.id, "Рассылка не принята.")

    await callback_query.answer()  # Убираем уведомление о нажатии
    await state.clear()  # Сброс состояния