from aiogram import types

start_markup = types.InlineKeyboardMarkup()
start_button_1 = types.InlineKeyboardButton("Заказать такси", callback_data='зак')
start_button_2 = types.InlineKeyboardButton("Мой аккаунт", callback_data='акк')
start_markup.add(start_button_1, start_button_2)


location_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
loc_button = types.KeyboardButton('Отправить мою локацию🌍', request_location=True)
location_markup.add(loc_button)

tel_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
tel_markup.add(types.KeyboardButton("Отправить номер телеофна, привязанный к Telegram", request_contact=True))


markup_confirm = types.InlineKeyboardMarkup()
conf = types.InlineKeyboardButton("Подтвердить", callback_data='1')
rej = types.InlineKeyboardButton("Отменить", callback_data= '0')
markup_confirm.add(conf, rej)








import re

def is_valid_phone_number(phone_number):
    # Проверка, что в строке нет букв
    if not re.match(r'^[0-9+\-() ]+$', phone_number):
        return False
    
    # Удаление всех символов, кроме цифр
    cleaned_number = re.sub(r'\D', '', phone_number)
    
    # Проверка, что номер содержит ровно 10 цифр
    if len(cleaned_number) == 10:
        return True
    
    # Проверка, что номер начинается с "+7" и содержит ровно 11 цифр
    elif cleaned_number.startswith('7') and len(cleaned_number) == 11:
        return True
    
    # Проверка, что номер начинается с "8" и содержит ровно 11 цифр
    elif cleaned_number.startswith('8') and len(cleaned_number) == 11:
        return True
    
    else:
        return False
    
def convert_to_digit(s):
    phone = re.sub(r'\D', '', s)
    if phone[0] == '7':
        return '+'+phone
    else:
        return '+7' + phone[1:]

