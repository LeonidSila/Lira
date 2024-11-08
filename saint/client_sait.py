import json

from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.enums.content_type import ContentType
from aiogram.enums.parse_mode import ParseMode
from database import data_base as db
from datetime import datetime


from create_bot import dp, bot, Admin, Chat

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

# chat_ids = {
#     "Срочные сообщения": 11473,
#     "Полезные ссылки": 3925,
#     "Месенджеры": 12649,
#     "Софт по другим радиостанциям": 715,
#     "ВЕДА": 11135,
#     "Гарантия Оборудование": 6279,
#     "Ретрансляторы ДМР Lira": 4927,
#     "Lira. Софт. Рекомендации . Обсуждения": 702,
#     "Дремучая дичь в установке антенн": 11423,
#     "Заказ раций, обмен, продажа": 6332,
#     "Ветерок Артгруппа": 11502,
#     "Организация связи. Настройки": 732,
#     "ZOV карты": 9504,
#     "Детекторы дронов. Оптимизация выбора": 10436,
#     "Антенны. Литература и информация": 8516,
#     "Глушилки. Дронов, связи и тд": 1655,
#     "Соседи": 7791,
#     "Анонс нового оборудования": 11674,
#     "Дроны": 745,
#     "ГРОЗА Программа корректировки огня": 6318,
#     "Решение для установки в технику": 3623,
#     "Софт Lira. Примеры прошивок": 3412,
#     "Дронница 2024": 15967,
#     "Не рэб средство индивидуальной защиты": 15710,
#     "Все по антеннам укв": 719,
#     "КЦПН Координационный Центр помощи": 11814,
#     "Артиллерия вопросы. Помощь профессионалов": 2723,
#     "Asel детектор дронов": 14961,
#     "NANO VNA": 7445,
#     "Борьба с FPV": 11302,
#     "KillCode": 5019,
#     "Памяти": 10200,
#     "Тактическая медицина": 12990,
#     "Радиомониторинг": 720,
#     "Крипта": 1071,
#     "Авиационная связь. И возможное взаимодействие": 934,
#     "ГПС Навигация. Полезный софт": 743,
#     "Вопросы в Академию связи": 11298,
#     "Предложения ВУЗов по нашей тематике": 11812,
#     "Репей Созвездие": 7901,
#     "Для добавления связистов и причастных, пишите": 10021,
#     "Сторонние ПО потРСТ": 5465,
#     "Новости в связи от противника": 8546,
#     "Полезная литература для связистов": 8511,
#     "Пожелания и негатив по Lira": 718,
#     "Сотник": 7214,
#     "При проблемах с РСТ. Гарантия": 1397,
#     "Маскировка объектов. Техники. Ложные": 2273,
#     "Периферия для раций. Обсуждение только": 3840,
#     "Обсуждение установок радиостанций": 835,
#     "Информация по наличию оборудования": 1838,
#     "Помехи связи противнику": 2685
# }

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

@router_client_sait.message(F.content_type == ContentType.WEB_APP_DATA)
async def parse_data(message: types.Message):
    data = json.loads(message.web_app_data.data)
    if 'themes' in data and 'message' in data and len(data) == 2:
        matched_topics = data['themes']
        text_user = str(data['message'])
        # Код для выполнения, если есть ключи 'themes' и 'message', и их всего 2
        # Рассылка с по темам 
        for topic_id in matched_topics:
            try:
                if topic_id in chat_ids_value:
                    await bot.send_message(chat_id=Chat.chat_id, text=text_user, message_thread_id=topic_id)
                else:
                    await bot.send_message(chat_id=Admin.Leonid, text= f"не найдена тема {topic_id}")
            except Exception as e:
                error_message = f"Ошибка при отправке сообщения в тему {topic_id}: {e}"
                print(error_message)
                await bot.send_message(chat_id=Admin.Leonid, text=error_message)
    
    elif 'message' in data and len(data) == 1:
        # Код для выполнения, если есть только ключ 'message'
        # Рассылка с чат бота
        try:
            message_user = data['message']
            db.cursor.execute('SELECT id FROM user')
            db.conn.commit()
            user_ids = db.cursor.fetchall()

            for user in user_ids:
                await bot.send_message(chat_id=user[0], text=message_user)
        except Exception as e:
            await bot.send_message(chat_id=Admin.Leonid, text=f"Ошибка при отправке сообщения: {e}")
        return "Выполнен код для 'message'."
    
    elif len(data) >= 3 and ('cutomerName' in data or 'product' in data):
        # Товары с сайта
        customer_name = data['customerName']
        
        additional_services = data['additionalServices']
        
        contactinfo = data['contactInfo']
        
        product_title = data['product']['title']
        
        # product_price = data['product']['price']
        
        formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        result = customer_name, additional_services, contactinfo, product_title
        
        await bot.send_message(chat_id=Admin.Leonid, text = f'Имя - <b>{result[0]}</b>\n\nДоп Услуга - <b>{result[1]}</b>\n\nКонтакты - <code>{result[2]}</code>\n\nПродукт по которому обратились - <b>{result[3]}</b>\n\nДата- <b>{formatted_date_time}</b>', parse_mode=ParseMode.HTML, reply_markup=types.ReplyKeyboardRemove())

    else:
        await bot.send_message(chat_id=Admin.Leonid, text="Получил данные с сайта но не смог обработать")
