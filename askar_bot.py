from aiogram import Bot, Dispatcher, types, executor
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from contextlib import suppress
from markups import *
import pickle
import pandas as pd

from aiogram.utils.exceptions import (MessageToEditNotFound, MessageCantBeEdited, MessageCantBeDeleted,
                                      MessageToDeleteNotFound)



TOKEN='6903931597:AAFB6D9PBxcTKCep3hK2daB8NdgMDZ_m5lA'
CHANEL_ID = "-1002012883717"
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


drivers = {}

try:
    D=pd.read_csv('D.csv', index_col=0)
except:
    D = pd.DataFrame(columns=["name", "auto_name", "gos_num", "count", "tel_num"])


try:
    P = pd.read_csv("P.csv", index_col=0)
except:
    P=pd.DataFrame(columns=['tel_num', 'count'],)

class OrderStates(StatesGroup):
    GetAdress = State()
    GetLocation = State()
    GetFinish = State()
    GetTel =State()
    ConfirmOrder = State()
    Success = State()
    Waiting = State()

class DriverState(StatesGroup):
    GetFIO = State()
    GetTelNum = State()
    GetAuto_name = State()
    GetGosNum = State()
    ConfirmOrder = State()


class Passanger:
    def __init__(self, pid):
        self.id = pid
        self.from_adres = None
        self.to_adres = None
        self.location = None
        self.tel_num = None

class Driver:
    def __init__(self, id):
        self.id = id
        self.name = None
        self.auto_name =None
        self.gos_num = None
        self.count = 0

d={}

print(D)
print(P)



@dp.message_handler(commands=['start'],state='*')
async def start(message, state):
    await message.answer(f'Привет, {message.chat.first_name}! Я бот такси. Я помогу тебе заказать такси', reply_markup= start_markup)
    await OrderStates.GetAdress.set()

@dp.callback_query_handler(lambda call: call.data == 'акк', state='*')
async def dips(call, state):
    id = call['from']['id']
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await call.message.delete()
    if id in P.index:
        pas = P.loc[id]
        await call.message.answer(f"Кол-во поездок: {pas['count']}")
    else:
        await call.message.answer("У вас пока что нет поездок")
    
    await state.finish()

@dp.callback_query_handler(lambda call: call.data=='зак', state=OrderStates.GetAdress)
async def get_adres(call, state):
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await call.message.delete()
    id = call['from']['id']
    d[id] = Passanger(id)
    await call.message.answer(f'Введите Ваш адресс')
    await OrderStates.GetLocation.set()
    

@dp.message_handler(state=OrderStates.GetLocation)
async def get_location(message, state):
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()
        await bot.delete_message(message.chat.id, message.message_id-1)
    id = message['from']['id']
    d[id].from_adres = message.text

    await message.answer("Отправьте свою локацию, для этого нажмите на кнопку ниже", reply_markup = location_markup)
    await OrderStates.GetFinish.set()

@dp.message_handler(content_types=types.ContentType.LOCATION, state=OrderStates.GetFinish)
async def get_finish(message, state):
    id = message['from']['id']
    d[id].location = message.location

    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()
        await bot.delete_message(message.chat.id, message.message_id-1)

    await message.answer("Куда вас отвести?")
    await OrderStates.GetTel.set()

@dp.message_handler(state=OrderStates.GetTel)
async def get_tel(message, state):
    id=message['from']['id']
    d[id].to_adres = message.text

    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()
        await bot.delete_message(message.chat.id, message.message_id-1)

    await message.answer("Введите номер телефона", reply_markup = tel_markup)
    await OrderStates.ConfirmOrder.set()

@dp.message_handler(content_types=types.ContentType.CONTACT, state=OrderStates.ConfirmOrder)
async def tel(message, state):
    id = message['from']['id']
    d[id].tel_num = convert_to_digit(message.contact.phone_number)
    pas = d[id]
    formatted_message = (
    f"<b>Ваш заказ:</b>\n"
    f"<i>Откуда:</i> <b>{pas.from_adres}\n</b>"
    f"<i>Куда:</i> <b>{pas.to_adres}\n</b>"
    f"<i>Номер телефона:</i> {pas.tel_num}"
)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()
        await bot.delete_message(message.chat.id, message.message_id-1)
    await message.answer(formatted_message, parse_mode= "HTML", reply_markup = markup_confirm)
    await OrderStates.Success.set()

@dp.message_handler(content_types=types.ContentType.TEXT, state=OrderStates.ConfirmOrder)
async def tel(message, state):
    id = message['from']['id']
    if is_valid_phone_number(message.text):
        d[id].tel_num = convert_to_digit(message.text)
        pas = d[id]
        formatted_message = (
        f"<b>Ваш заказ:</b>\n"
        f"<i>Откуда:</i> <b>{pas.from_adres}\n</b>"
        f"<i>Куда:</i> <b>{pas.to_adres}\n</b>"
        f"<i>Номер телефона:</i> {pas.tel_num}"
    )
        with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
            await message.delete()
            await bot.delete_message(message.chat.id, message.message_id-1)
        await message.answer(formatted_message, parse_mode= "HTML", reply_markup = markup_confirm)
        await OrderStates.Success.set()
    else:
        await message.answer("Вы ввели некорректный номер телефона. Пожалуйста, введите другой.")


@dp.callback_query_handler(lambda call: call.data == '1', state=OrderStates.Success)
async def confirm_order(call, state):
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await call.message.delete()
    id=call['from']['id']
    pas = d[id]
    formatted_message = (
    f"<i>Откуда:</i> <b>{pas.from_adres}\n</b>"
    f"<i>Куда:</i> <b>{pas.to_adres}\n</b>"
    f"<i>Номер телефона:</i> {pas.tel_num}")

    await call.message.answer(f"<b>Ваш заказ:</b>\n"+formatted_message, parse_mode = 'HTML')
    await call.message.answer("Ищем водителя...🔎\nКак только найдем, сразу же отправим вам сообщение.")
    await OrderStates.Waiting.set()

    chanel_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Взять заказ", callback_data="@"+str(id)))
    await bot.send_message(CHANEL_ID, formatted_message, parse_mode='HTML', reply_markup=chanel_markup)

class DriverStates(StatesGroup):
    Start = State()

@dp.callback_query_handler(lambda call: call.data[0] =='@', state = '*')
async def take_order(call, state):
    id = call['from']['id']
    if id in D.index:
        pas_id = int(call.data[1:])
        with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
            await call.message.delete()

        markup_arrived = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Подъехал", callback_data="#"+str(pas_id)))
        driver_info = D.loc[id]

        await bot.send_message(pas_id, "🚕Ваш заказ принят🚕\nВодитель уже в пути")
        await bot.send_sticker(pas_id, 'CAACAgUAAxkBAAECprNljoogWWGO9pFvHGL7-1T7BJY-dAACrgIAAsMX6VRLN8FunfjfiDQE')
        await bot.send_message(pas_id, f"<b>Информация о водителеℹ\nФИО:</b> {driver_info['name']}\n<b>Номер телефона:</b> {driver_info['tel_num']}\n<b>Инфо о машине:</b> {driver_info['auto_name']}\n<b>ГосНомер:</b> {driver_info['gos_num']}", parse_mode='HTML')
        await bot.send_location(id, d[pas_id].location.latitude, d[pas_id].location.longitude)
        await bot.send_message(call['from']['id'], "Ваш заказ:\n"+call.message.text, parse_mode='HTML', reply_markup=markup_arrived)
    else:
        await bot.send_message(id, "Вы не зарегестрированы! Нажмите /new_driver")


@dp.callback_query_handler(lambda call: call.data[0] == '#', state="*")
async def driver_come(call, state):
    pas_id = int(call.data[1:])
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await call.message.delete()

    markup_finish = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Завершить поездку", callback_data="^"+str(pas_id)))

    await call.message.answer(call.message.text, reply_markup=markup_finish)
    await bot.send_message(pas_id, "🚖Водитель ожидает вас🚖\nМожете выходить")



@dp.callback_query_handler(lambda call: call.data[0] == '^', state="*")
async def finish_road(call, state):
    pas_id = int(call.data[1:])
    driv_id = call['from']['id']

    D.at[driv_id, 'count']+=1

    pas = d[pas_id]
   

    if pas_id not in P.index:
        P.loc[pas_id] = [pas.tel_num, 0]
    
    P.at[pas_id, 'count'] += 1
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await call.message.delete()

    await call.message.answer(f"+1 поездка. Всего поездок: {D.loc[driv_id]['count']}")

    await bot.send_message(pas_id, "Мы приехали! Спасибо что выбрали нас🎈")
    D.to_csv('D.csv', index=True)
    P.to_csv('P.csv', index=True)









@dp.message_handler(commands=['new_driver'], state='*')
async def driver_sign_in(message, state):
    await message.answer("Введите ФИО")
    id = message['from']['id']
    drivers[id]=Driver(id)
    await DriverState.GetFIO.set()

@dp.message_handler(state=DriverState.GetFIO)
async def driver_FIO(message, state):
    id = message['from']['id']
    if len(message.text.split()) == 3:
        drivers[id].name=message.text
        with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
            await message.delete()
            await bot.delete_message(message.chat.id, message.message_id-1)
        await DriverState.GetTelNum.set()
        await message.answer("Нажмите на кнопку ниже, чтобы отправить номер телефона", reply_markup=tel_markup)
    else:
        await message.answer("Введите корректные данные")

@dp.message_handler(content_types=types.ContentType.CONTACT, state=DriverState.GetTelNum)
async def driver_tel(message, state):
    id = message['from']['id']
    drivers[id].tel_num = convert_to_digit(message.contact.phone_number)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()
        await bot.delete_message(message.chat.id, message.message_id-1)
    await message.answer("Введите назвние машины, цвет")
    await DriverState.GetAuto_name.set()

@dp.message_handler(state=DriverState.GetAuto_name)
async def auto_name(message, state):
    id = message['from']['id']
    drivers[id].auto_name = message.text
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()
        await bot.delete_message(message.chat.id, message.message_id-1)
    await message.answer("Введите ГосНомер, пример A999ББ")
    await DriverState.GetGosNum.set()

@dp.message_handler(state=DriverState.GetGosNum)
async def get_gos_num(message, state):

    id = message['from']['id']
    drivers[id].gos_num = message.text
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()
        await bot.delete_message(message.chat.id, message.message_id-1)
    await message.answer(f'Проверьте данные:\nФИО: {drivers[id].name}\nНомер телефона: {drivers[id].tel_num}\n Инфо о машине: {drivers[id].auto_name}\n ГосНомер: {drivers[id].gos_num}', reply_markup=markup_confirm)
    await DriverState.ConfirmOrder.set()

@dp.callback_query_handler(lambda call: call.data == '1', state=DriverState.ConfirmOrder)
async def confirm_driver(call, state):
    id = call['from']['id']
    driver = drivers[id]
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await call.message.delete()
    await call.message.answer(f'ФИО: {drivers[id].name}\nНомер телефона: {drivers[id].tel_num}\n Инфо о машине: {drivers[id].auto_name}\n ГосНомер: {drivers[id].gos_num}')
    if id in D.index:
        D.drop([id], inplace=True)

    D.loc[driver.id] = [driver.name, driver.auto_name, driver.gos_num, driver.count, driver.tel_num]
    D.to_csv('D.csv', index=True)
    
    del drivers[id]
    await call.message.answer("Вы Зарегистрированы!")
    await state.finish()
    print(D)

@dp.callback_query_handler(lambda call:call.data == '0', state=DriverState.ConfirmOrder)
async def zero_conf(call, state):
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await call.message.delete()
    await call.message.answer("Если хотите начать сначала введите /new_driver")










executor.start_polling(dp)
