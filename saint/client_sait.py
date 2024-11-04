import json

from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.enums.content_type import ContentType
from aiogram.enums.parse_mode import ParseMode

from datetime import datetime

from create_bot import dp, bot, Admin

router_client_sait = Router()

now = datetime.now()

@router_client_sait.message(F.content_type == ContentType.WEB_APP_DATA)
async def parse_data(message: types.Message):
    data = json.loads(message.web_app_data.data)
    
    customer_name = data['customerName']
    
    additional_services = data['additionalServices']
    
    contactinfo = data['contactInfo']
    
    product_title = data['product']['title']
    
    # product_price = data['product']['price']
    
    formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    result = customer_name, additional_services, contactinfo, product_title
    
    await bot.send_message(chat_id=Admin.Leonid, text = f'Имя - <b>{result[0]}</b>\n\nДоп Услуга - <b>{result[1]}</b>\n\nКонтакты - <code>{result[2]}</code>\n\nПродукт по которому обратились - <b>{result[3]}</b>\n\nДата- <b>{formatted_date_time}</b>', parse_mode=ParseMode.HTML, reply_markup=types.ReplyKeyboardRemove())
