# -*- coding: utf-8 -*-
###------------------------------------------------------------------------------------------------Билиотека
import io
import sys
import time
import random
import lxml
import requests
from bs4 import BeautifulSoup
import config
import logging
from contextlib import suppress
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
import re
import os
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageOps, ImageDraw2, ImageChops
from aiogram.types import InputFile, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import pandas
import vk_api
import json
import asyncio
import sqlite3
from aiogram.utils.exceptions import (MessageToEditNotFound, MessageCantBeEdited, MessageCantBeDeleted,MessageToDeleteNotFound)
import traceback
import nest_asyncio
import datetime, threading, time
from pyqiwip2p import QiwiP2P
from pyqiwip2p.types import QiwiCustomer, QiwiDatetime
from datetime import timedelta, date
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types, executor
import warnings
###------------------------------------------------------------------------------------------------ DB
connect = sqlite3.connect('other/GlazIntim.db')
admin_panel = connect.cursor()
admin_panel.execute('CREATE TABLE IF NOT EXISTS admin_panel_info(number_code TEXT NOT NULL,token_vk_bot TEXT NOT NULL, full_price TEXT NOT NULL, vremen_price TEXT NOT NULL, number_qiwi TEXT NOT NULL, proxy_vk TEXT NOT NULL)')
###------------------------------------------------------------------------------------------------
workers = sqlite3.connect('other/worker.db')
user_workers = workers.cursor()
#user_workers.execute('CREATE TABLE IF NOT EXISTS user_workers(id_user INTEGER, time_register TEXT NOT NULL, status_active INTEGER, status_worker INTEGER, worker_referal INTEGER, balanse_worker FLOAT, qiwi_rekv_worker TEXT NOT NULL)')
##-----------------------------
nest_asyncio.apply()
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=config.token_bot_worker)
dp = Dispatcher(bot, storage=storage)
channel_id = config.channel_id
channel_id_zalet = config.channel_id_zalet
###--------------------------------

###------------------------------------------------------------------------------------------------ States
class Form(StatesGroup):
    vk_add = State()  # Работа с вк
    insta_add = State()  # Работа с инстой
    telega_add = State()  # Работа с телега
    full_dostup_state = State()  # Работа с полным доступом оплат
    vremen_dostup_state = State()  # Работа с временным доступом
    vk_token_add = State() # Админка
    qiwi_num_add = State()# Админка
    ful_adm = State()# Админка
    vrem_adm = State()# Админка
    proxy_adm = State()#Админка
    worker_add = State()#Админка
    worker_dell = State()#Админка
    update_worker_qiwi = State()#Обновить киви
###------------------------------------------------------------------------------------------------ Keyboards
work_main = KeyboardButton('👨🏼‍🏫 Мой кабинет')
info_main = KeyboardButton('📗️ Информация')
main = ReplyKeyboardMarkup(resize_keyboard=True)
main.row (work_main,info_main)
###------------ key
vk_inlain = InlineKeyboardButton('♦𝗩𝗞.𝗖𝗢𝗠', callback_data='vk_button')
telegram_inlain = InlineKeyboardButton('♦𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗠', callback_data='telegram_button')
insta_inlain = InlineKeyboardButton('♦𝗜𝗡𝗦𝗧𝗔𝗚𝗥𝗔𝗠', callback_data='insta_button')
inline_vibor = InlineKeyboardMarkup(resize_keyboard=True)
inline_vibor.add (vk_inlain)
inline_vibor.add (telegram_inlain)
inline_vibor.add (insta_inlain)
###------------ key
prov_oplat = KeyboardButton('💷  Проверить оплату')
prov_oplat_back = KeyboardButton('🔙 Вернуться в главное меню')
prov_oplat_but = ReplyKeyboardMarkup(resize_keyboard=True)
prov_oplat_but.add (prov_oplat)
prov_oplat_but.row (prov_oplat_back)
###------------ key
prov_oplat_back_main = KeyboardButton('🔙 Вернуться в главное меню')
prov_oplat_but_but = ReplyKeyboardMarkup(resize_keyboard=True)
prov_oplat_but_but.row (prov_oplat_back_main)
###------------ key
back_main = KeyboardButton('🏡 Вернуться в главное меню')
back_main_but = ReplyKeyboardMarkup(resize_keyboard=True)
back_main_but.add (back_main)
###------------ ADMIN
poisk_back_main = KeyboardButton('👁 Указать другой адрес')
poisk_back_but = ReplyKeyboardMarkup(resize_keyboard=True)
poisk_back_but.add (poisk_back_main)
###------------
token_vk_admin = KeyboardButton('👁 Токен аккаунта вк')
prox_admin = KeyboardButton('👁 Прокся для токена вк')
full_admin = KeyboardButton('👁 Цена полного доступа')
mai_admin = KeyboardButton('👁 Цена временного доступа')
add_worker = KeyboardButton('👁 Вернуть должность воркеру')
del_worker = KeyboardButton('👁 Снять с должности воркера')
admin_btn = ReplyKeyboardMarkup(resize_keyboard=True)
admin_btn.row (token_vk_admin,prox_admin)
admin_btn.row (full_admin,mai_admin)
admin_btn.row (add_worker, del_worker)
###--------------
###------------
add_work = KeyboardButton('😌 Вернуть должность воркеру')
del_worker2 = KeyboardButton('😌 Снять с должности воркера')
moder_btn = ReplyKeyboardMarkup(resize_keyboard=True)
moder_btn.row (add_work )
moder_btn.row (del_worker2)
###--------------
poisk_back_main_vk = KeyboardButton('🔍 Указать другой адрес')
poisk_back_but_vk = ReplyKeyboardMarkup(resize_keyboard=True)
poisk_back_but_vk.add (poisk_back_main_vk)
###--------------
###------------------------------------------------------------------------------------------------ start
async def delete_message(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    datetime_user = date.today()
    user_workers.execute(f"SELECT id_user, status_worker FROM user_workers where id_user ={message.from_user.id}")
    db_worker = user_workers.fetchone()
    if db_worker == None:
        user_workers.execute(f"INSERT INTO user_workers VALUES ({message.from_user.id}, '{datetime_user}', 1, 1, 0, 0, 0)")
    else:
        pass
    workers.commit()
    img = open('temp/image_interface/work_menu_img.png', 'rb')
    await bot.send_photo(message.chat.id, img, caption='''👑 <strong>Добро пожаловать в команду!</strong>\n\n💼 Все мануалы и прочее собраны в <strong>информации бота</strong>.\n\n💼 <strong>Суть работы: </strong>\n\n—В нашей команде имеется бот по <strong>фейк-поиску интимок🔞</strong>\n—Чтобы человек получил <strong>"Слив интимок человека"</strong>, ему нужно <strong>оплатить доступ.</strong>\n—Бот имеет <strong>полный доступ и временный.</strong>\n\nНа данный момент в <strong>2022 году схема свежая</strong> и развести мамонта очень просто.\n\nВы будете получать <strong>уведомление, если мамонт оплатил или авторизировался</strong>.\n\nПрошу заметить, если вы были <strong>сняты с должности</strong> и мамонт переходит по вашей ссылке, то после залета мамонта <strong>вам будет начислен баланс</strong>, но снять вы не сможете, до тех пор пока <strong>не вернете свою должность</strong>\n\nПоэтому просим вас не нарушать правила''', parse_mode='HTML', reply_markup=main)

@dp.message_handler(commands=['admin'], user_id=int(config.Admin_id))
async def admin(message: types.Message):
    admin_register = config.Admin_id
    img = open('temp/image_interface/admin_img.png', 'rb')

    admin_panel.execute(f"SELECT number_code, token_vk_bot, full_price, vremen_price, number_qiwi FROM admin_panel_info where number_code={admin_register}")
    db_admin_panel = admin_panel.fetchone()
    connect.commit()
    s = requests.Session()
    s.proxies.update({'http': str(admin_panel.execute(f"SELECT proxy_vk, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0])})
    token_vk = str(admin_panel.execute(f"SELECT token_vk_bot, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0])
    vk_session = vk_api.VkApi(token=token_vk, session=s)
    try:
        vk = vk_session.get_api()
        status = vk_session.method("status.get", {"user_id": 1})
        vk_checker = "🟢 Online"
    except:
        vk_checker = "🔴 Offline (Неверный токен, либо IP-Прокси)"
    await bot.send_photo(message.chat.id, img, caption=f'📱 Добро пожаловать в админ-панель бота\n\n🔑Проверка токена вк\n🦊Статус токена: {vk_checker}\n🦊Чтобы проверить новый токен напишите /admin\n\n👨‍💻 Воркеров: {user_workers.execute(f"SELECT COUNT( * ) FROM  user_workers WHERE status_worker = 1").fetchone()[0]}\n👨‍💻 Пользователей в основном скам боте всего: {admin_panel.execute(f"SELECT COUNT( * ) FROM  user_intim").fetchone()[0]}\n👨‍💻 Проверено сливов VK (женских): {admin_panel.execute(f"SELECT COUNT( * ) FROM  vk_information").fetchone()[0]}\n👨‍💻 Проверено сливов instagram: {admin_panel.execute(f"SELECT COUNT( * ) FROM  insta_information").fetchone()[0]}\n👨‍💻 Проверено сливов telegram: {admin_panel.execute(f"SELECT COUNT( * ) FROM  telega_information").fetchone()[0]}\n\nВ данной панели вы сможете изменить:\n👁Токен аккаунта вк\n👁Цены доступов\n👁Аунтификационный номер для оплаты\получения платежа\n\nЧтобы перейти снова к боту напишите /start\n', parse_mode='HTML', reply_markup=admin_btn)
    pass

@dp.message_handler(commands=['moderator'], user_id=int(config.Moderator_id))
async def admin(message: types.Message):
    img = open('temp/image_interface/moder_img.png', 'rb')
    admin_panel.execute(f"SELECT number_code, token_vk_bot, full_price, vremen_price, number_qiwi FROM admin_panel_info where number_code={config.Admin_id}")
    db_admin_panel = admin_panel.fetchone()
    connect.commit()
    s = requests.Session()
    s.proxies.update({'http': str(admin_panel.execute(f"SELECT proxy_vk, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0])})
    token_vk = str(admin_panel.execute(f"SELECT token_vk_bot, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0])
    vk_session = vk_api.VkApi(token=token_vk, session=s)
    try:
        vk = vk_session.get_api()
        status = vk_session.method("status.get", {"user_id": 1})
        vk_checker = "🟢 Online"
    except:
        vk_checker = "🔴 Offline (Неверный токен, либо IP-Прокси)"
    await bot.send_photo(message.chat.id, img, caption=f'📱 Добро пожаловать в модер-панель бота\n\n👨‍💻 Воркеров: {user_workers.execute(f"SELECT COUNT( * ) FROM  user_workers WHERE status_worker = 1").fetchone()[0]}\n👨‍💻 Пользователей в основном скам боте всего: {admin_panel.execute(f"SELECT COUNT( * ) FROM  user_intim").fetchone()[0]}\n👨‍💻 Проверено сливов VK (женских): {admin_panel.execute(f"SELECT COUNT( * ) FROM  vk_information").fetchone()[0]}\n👨‍💻 Проверено сливов instagram: {admin_panel.execute(f"SELECT COUNT( * ) FROM  insta_information").fetchone()[0]}\n👨‍💻 Проверено сливов telegram: {admin_panel.execute(f"SELECT COUNT( * ) FROM  telega_information").fetchone()[0]}\n\nВ данной панели вы сможете изменить:\n👁Вернуть должность воркеру\n👁Снять с должности воркера\n\nЧтобы перейти снова к боту напишите /start\n', parse_mode='HTML', reply_markup=moder_btn)
    pass
###--------------------------------------------------------
@dp.message_handler(lambda message: message.text == "👁 Токен аккаунта вк", user_id=int(config.Admin_id))
async def process_login(message: types.Message):
    await message.answer("👁 Укажите новый токен аккаунта вк")
    await Form.vk_token_add.set()
    pass

@dp.message_handler(lambda message: message.text == "👁 Вернуть должность воркеру", user_id=int(config.Admin_id))
async def process_login(message: types.Message):
    await message.answer("👁 ID воркера, которого нужно вернуть")
    await Form.worker_add.set()
    pass

@dp.message_handler(lambda message: message.text == "😌 Вернуть должность воркеру", user_id=int(config.Moderator_id))
async def process_login(message: types.Message):
    await message.answer("👁 ID воркера, которого нужно вернуть")
    await Form.worker_add.set()
    pass

@dp.message_handler(lambda message: message.text == "👁 Снять с должности воркера", user_id=int(config.Moderator_id))
async def process_login(message: types.Message):
    await message.answer("👁 ID воркера, которого нужно снять")
    await Form.worker_dell.set()
    pass

@dp.message_handler(lambda message: message.text == "😌 Снять с должности воркера", user_id=int(config.Moderator_id))
async def process_login(message: types.Message):
    await message.answer("👁 ID воркера, которого нужно снять")
    await Form.worker_dell.set()
    pass

@dp.message_handler(lambda message: message.text == "👁 Прокся для токена вк", user_id=int(config.Admin_id))
async def process_login(message: types.Message):
    await message.answer("👁 Укажите проксю для токена. Она послужит для корректного подключения к сессии\nНужен тип - HTTP\nПример: http://176.193.164.85:53281")
    await Form.proxy_adm.set()
    pass

@dp.message_handler(lambda message: message.text == "👁 QiwiP2P", user_id=int(config.Admin_id))
async def process_login(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id - 1)
    await message.answer("👁 Укажите аунтификационные данные Qiwi\n\nПолучить адрес: https://qiwi.com/p2p-admin/transfers/api\nЛистаете в самый низ -> Создать пару ключей и настроить -> Вписываете любое наименование -> Получаете код(Именно код, который в оранжевой рамочке)")
    await Form.qiwi_num_add.set()
    pass

@dp.message_handler(lambda message: message.text == "👁 Цена полного доступа", user_id=int(config.Admin_id))
async def process_login(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id - 1)
    await message.answer("👁 Укажите цену полного доступа")
    await Form.ful_adm.set()
    pass

@dp.message_handler(lambda message: message.text == "👁 Цена временного доступа", user_id=int(config.Admin_id))
async def process_login(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id - 1)
    await message.answer("👁 Укажите цену временного доступа")
    await Form.vrem_adm.set()
    pass
####--------------------------
@dp.message_handler(state=Form.vk_token_add)
async def register_vk_token(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['vk_token_add'] = message.text
    await Form.next()
    info = data['vk_token_add']
    admin_panel.execute(f"UPDATE admin_panel_info SET token_vk_bot='{info}' WHERE number_code={config.Admin_id}")
    connect.commit()
    await message.answer(f'✅ ВК токен обновлен', reply_markup=admin_btn)
    await state.finish()
    pass

@dp.message_handler(state=Form.worker_add)
async def register_vk_token(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['worker_add'] = message.text
    await Form.next()
    info = data['worker_add']
    user_workers.execute(f"UPDATE user_workers SET status_worker = '1' WHERE id_user = {info}")
    workers.commit()
    await message.answer(f'✅ Статус воркера был обновлен')
    await state.finish()
    pass

@dp.message_handler(state=Form.worker_dell)
async def register_vk_token(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['worker_dell'] = message.text
    await Form.next()
    info = data['worker_dell']
    user_workers.execute(f"UPDATE user_workers SET status_worker = '0' WHERE id_user = {info}")
    workers.commit()
    await message.answer(f'✅ Статус воркера был обновлен')
    await state.finish()
    pass

@dp.message_handler(state=Form.proxy_adm)
async def register_vk_token(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['proxy_adm'] = message.text
    await Form.next()
    info = data['proxy_adm']
    admin_panel.execute(f"UPDATE admin_panel_info SET proxy_vk='{info}' WHERE number_code={config.Admin_id}")
    connect.commit()
    await message.answer(f'✅ Прокся для вк обновлена', reply_markup=admin_btn)
    await state.finish()
    pass

@dp.message_handler(state=Form.qiwi_num_add)
async def register_vk_token(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['qiwi_num_add'] = message.text
    await Form.next()
    info = data['qiwi_num_add']
    admin_panel.execute(f"UPDATE admin_panel_info SET number_qiwi='{info}' WHERE number_code={config.Admin_id}")
    connect.commit()
    await message.answer(f'✅ Новый аунтификационный номер Qiwi обновлен', reply_markup=admin_btn)
    await state.finish()
    pass

@dp.message_handler(state=Form.ful_adm)
async def register_vk_token(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['ful_adm'] = message.text
    await Form.next()
    info = data['ful_adm']
    admin_panel.execute(f"UPDATE admin_panel_info SET full_price='{info}' WHERE number_code={config.Admin_id}")
    connect.commit()
    await message.answer(f'✅ Цена на полный доступ обновлена', reply_markup=admin_btn)
    await state.finish()
    pass
@dp.message_handler(state=Form.vrem_adm)
async def register_vk_token(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['vrem_adm'] = message.text
    await Form.next()
    info = data['vrem_adm']
    admin_panel.execute(f"UPDATE admin_panel_info SET vremen_price='{info}' WHERE number_code={config.Admin_id}")
    connect.commit()
    await message.answer(f'✅ Цена на временный доступ обновлена', reply_markup=admin_btn)
    await state.finish()
    pass

@dp.message_handler(lambda message: message.text == "👨🏼‍🏫 Мой кабинет")
async def worker_profile(message: types.Message):
    vivod_balanse= InlineKeyboardButton('Вывести баланс!',callback_data='vivod_balanse')
    update_qiwi_worker = InlineKeyboardButton('Указать свой QIWI!',callback_data='update_qiwi_worker')
    workers_btn = InlineKeyboardMarkup(resize_keyboard=True)
    workers_btn.row(vivod_balanse,update_qiwi_worker)
    user_workers.execute(f"SELECT id_user, status_worker FROM user_workers where status_worker = 0 AND id_user = {message.from_user.id}")
    db_worker = user_workers.fetchone()
    if db_worker == None:
        img = open('temp/image_interface/my_profile.png', 'rb')

        adres = str(config.AdressBot)
        worker_url = adres.replace("@", "")
        await bot.send_photo(message.chat.id, img, caption=f'''💻<strong>Профиль воркера</strong>\n\n<strong>💳Ваш баланс:</strong> {user_workers.execute(f"SELECT balanse_worker, id_user FROM user_workers WHERE id_user = {message.from_user.id}").fetchone()[0]}₽\n<strong>🦣 Количество ваших мамонтов:</strong> {user_workers.execute(f"SELECT count (*) FROM user_workers WHERE worker_referal = {message.from_user.id}").fetchone()[0]} шт.\n\n<strong>‼️‼️‼️ Обязательно перейти в бота, для получения уведомлений:</strong> '''+config.AdressBot+''' и нажать <strong>"Старт"</strong>\n\n<strong>💎 Начать работать:</strong>\n<strong>💻Ваш ID:</strong>'''+str(message.from_user.id)+'''\n\n<strong>🔗 Ваша ссылка:</strong> <code>https://t.me/''' + str(worker_url) + '''?start=''' + str(message.from_user.id) + '''</code>\n\n💰 Приглашайте мамонтов по своей ссылке в бота и заставьте его <strong>любым образом оплатить подписку</strong>\n\n🥳 Все залеты отображается на канале -'''+ str(config.zalet_adress), parse_mode='HTML', reply_markup=workers_btn)
        pass
    else:
        await message.answer('Вы были сняты с должности')
        pass

@dp.message_handler(lambda message: message.text == "📗️ Информация")
async def worker_profile(message: types.Message):
    user_workers.execute(f"SELECT id_user, status_worker FROM user_workers where status_worker = 0 AND id_user = {message.from_user.id}")
    db_worker = user_workers.fetchone()
    if db_worker == None:
        img = open('temp/image_interface/info_img.png', 'rb')
        adres = str(config.AdressBot)
        await bot.send_photo(message.chat.id, img, caption=f'''💈 <strong>Добро пожаловать в информационный раздел!</strong>\n\n🎀 Мануал - '''+str(config.manual)+'''\n\n└Связь с Админом: '''+str(config.call_admin)+'''\n└Связь с Модератором: '''+str(config.call_moder)+'''\n\n💈 Ниже присутствует информация проекта.\n└👊 Активных воркеров: <strong>'''+str(user_workers.execute(f"SELECT COUNT( * ) FROM  user_workers WHERE status_worker = 1").fetchone()[0])+'''</strong>\n└ ✌️Всего пользователей в ботах: <strong>'''+str(user_workers.execute(f"SELECT COUNT( * ) FROM  user_workers").fetchone()[0])+'''</strong>''', parse_mode='HTML')
        pass
    else:
        await message.answer('Вы были сняты с должности')
        pass

@dp.callback_query_handler(text='update_qiwi_worker')
async def process_callback_vivod_balanse(callback_query: types.CallbackQuery):
    img = open('temp/image_interface/update_rekvi_work.png', 'rb')
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer_photo(photo=img,caption=f'🔹 Укажите свои QIWI реквизиты\n\n📱Указывать нужно ваш номер\n📝На данный номер будет приходить вывод баланса')
    await Form.update_worker_qiwi.set()

@dp.callback_query_handler(text='vivod_balanse')
async def process_callback_vivod_balanse(callback_query: types.CallbackQuery):
    img = open('temp/image_interface/vivod_balanse_worker.png', 'rb')
    await bot.answer_callback_query(callback_query.id)
    zero_balanse = user_workers.execute(f"SELECT balanse_worker, id_user FROM user_workers where id_user = {callback_query.from_user.id}").fetchone()[0]
    if zero_balanse == 0:
        await callback_query.message.answer_photo(photo=img, caption=f'🥺Уважаемый воркер, у вас на балансе 0 рублей.', parse_mode='HTML', reply_markup=main)
    else:
        balanse_vivod = user_workers.execute(f"SELECT balanse_worker, id_user FROM user_workers where id_user = {callback_query.from_user.id}").fetchone()[0]
        num_qiwi_worker = user_workers.execute(f"SELECT qiwi_rekv_worker, id_user FROM user_workers where id_user = {callback_query.from_user.id}").fetchone()[0]
        user_workers.execute(f"UPDATE user_workers SET balanse_worker='0.0' WHERE id_user={callback_query.from_user.id}")
        workers.commit()
        await callback_query.message.answer_photo(photo=img, caption=f'💳 Весь ваш баланс будет выведен на указанные ранее реквизиты\n✅ Сообщение с запросом успешно отправлено\n\nЕсли вы забыли указать свои реквизиты отпишите Администратору, либо Модератору',parse_mode='HTML', reply_markup=main)
        await bot.send_message(channel_id,f"💳Воркер запросил вывод\nID воркера " + str(callback_query.from_user.id) + "\n\nQiwi номер:"+str(num_qiwi_worker)+"\nСумма вывода: "+str(balanse_vivod)+" рублей")

@dp.message_handler(state=Form.update_worker_qiwi)
async def register_vk_token(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['update_worker_qiwi'] = message.text
    await Form.next()
    info = data['update_worker_qiwi']
    user_workers.execute(f"UPDATE user_workers SET qiwi_rekv_worker='{info}' WHERE id_user={message.from_user.id}")
    workers.commit()
    await message.answer(f'✅ Ревизиты вашего киви были обновлены', reply_markup=main)
    await state.finish()
    pass

###-------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

