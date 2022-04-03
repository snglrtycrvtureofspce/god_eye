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
from aiogram.types import ParseMode, InlineKeyboardMarkup
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
user_intim = connect.cursor()
user_intim.execute('CREATE TABLE IF NOT EXISTS user_intim(id_tel_user INTEGER, time_register TEXT NOT NULL)')
vk_information_baby = connect.cursor()
vk_information_baby.execute('CREATE TABLE IF NOT EXISTS vk_information(id_vk_id TEXT NOT NULL, intim_photo TEXT NOT NULL, mess TEXT NOT NULL, nig_mess TEXT NOT NULL, ghost_friends TEXT NOT NULL)')
insta_information = connect.cursor()
insta_information.execute('CREATE TABLE IF NOT EXISTS insta_information(id_insta TEXT NOT NULL, intim_photo TEXT NOT NULL, mess TEXT NOT NULL, nig_mess TEXT NOT NULL, img TEXT NOT NULL)')
telega_information = connect.cursor()
telega_information.execute('CREATE TABLE IF NOT EXISTS telega_information(id_telega TEXT NOT NULL, intim_photo TEXT NOT NULL, mess TEXT NOT NULL, nig_mess TEXT NOT NULL, img TEXT NOT NULL)')
admin_panel = connect.cursor()
admin_panel.execute('CREATE TABLE IF NOT EXISTS admin_panel_info(number_code TEXT NOT NULL,token_vk_bot TEXT NOT NULL, full_price TEXT NOT NULL, vremen_price TEXT NOT NULL, number_qiwi TEXT NOT NULL, proxy_vk TEXT NOT NULL)')
###------------------------------------------------------------------------------------------------
workers = sqlite3.connect('other/worker.db')
user_workers = workers.cursor()
user_workers.execute('CREATE TABLE IF NOT EXISTS user_workers(id_user INTEGER, time_register TEXT NOT NULL, status_active INTEGER, status_worker INTEGER, worker_referal INTEGER, balanse_worker FLOAT, qiwi_rekv_worker TEXT NOT NULL)')
##-----------------------------
nest_asyncio.apply()
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=config.token)
dp = Dispatcher(bot, storage=storage)
channel_id = config.channel_id
channel_id_zalet = config.channel_id_zalet
###--------------------------------
admin_panel.execute(f"SELECT number_code, token_vk_bot, full_price, vremen_price, number_qiwi, proxy_vk FROM admin_panel_info where number_code={config.Admin_id}")
db_admin_panel = admin_panel.fetchone()
if db_admin_panel == None:
    admin_panel.execute(f"INSERT INTO admin_panel_info VALUES ({config.Admin_id}, 'create', 'by', 'ober', 'DateBase', 'sex')")
else:
    pass
user_workers.execute(f"SELECT id_user, time_register, status_active, status_worker, worker_referal FROM user_workers where id_user=1")
user_workers_panel = user_workers.fetchone()
if user_workers_panel == None:
    user_workers.execute(f"INSERT INTO user_workers VALUES (1, 'я root,меня не удалять', 3, 1, 0, 0, 0)")
else:
    pass
aut = admin_panel.execute(f"SELECT number_qiwi, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]
p2p = QiwiP2P(auth_key=aut)
now = datetime.datetime.now()
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
    message_send_all = State()#Админка
###------------------------------------------------------------------------------------------------ Keyboards
poisk_main = KeyboardButton('🔍 Начать поиск')
prof_main = KeyboardButton('🕵️‍♀️ Мой профиль')
buy_main = KeyboardButton('👜 Мои покупки')
otziv_main = KeyboardButton('📚 Отзывы')
main = ReplyKeyboardMarkup(resize_keyboard=True)
main.row (poisk_main,prof_main)
main.row (buy_main,otziv_main)
###------------ key
vk_inlain = InlineKeyboardButton('♦𝗩𝗞.𝗖𝗢𝗠', callback_data='vk_button')
telegram_inlain = InlineKeyboardButton('♦𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗠', callback_data='telegram_button')
insta_inlain = InlineKeyboardButton('♦𝗜𝗡𝗦𝗧𝗔𝗚𝗥𝗔𝗠', callback_data='insta_button')
inline_vibor = InlineKeyboardMarkup(resize_keyboard=True)
inline_vibor.add (vk_inlain)
inline_vibor.add (telegram_inlain)
inline_vibor.add (insta_inlain)
###------------ key
prov_oplat_back = KeyboardButton('🏡 Вернуться в главное меню')
prov_oplat_but = ReplyKeyboardMarkup(resize_keyboard=True)
prov_oplat_but.row (prov_oplat_back)
###------------ key
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
qiwi_admin = KeyboardButton('👁 QiwiP2P')
token_vk_admin = KeyboardButton('👁 Токен аккаунта вк')
prox_admin = KeyboardButton('👁 Прокся для токена вк')
full_admin = KeyboardButton('👁 Цена полного доступа')
mai_admin = KeyboardButton('👁 Цена временного доступа')
sendall_admin = KeyboardButton('📣 Рассылка сообщений')
admin_btn = ReplyKeyboardMarkup(resize_keyboard=True)
admin_btn.add (qiwi_admin)
admin_btn.row (token_vk_admin,prox_admin)
admin_btn.row (full_admin,mai_admin)
admin_btn.add (sendall_admin)
###--------------
poisk_back_main_vk = KeyboardButton('🔍 Указать другой адрес')
poisk_back_but_vk = ReplyKeyboardMarkup(resize_keyboard=True)
poisk_back_but_vk.add (poisk_back_main_vk)
###--------------
###------------------------------------------------------------------------------------------------ start
async def check_status(phone, token):
    ses = requests.Session()
    ses.headers['authorization'] = 'Bearer ' + token
    parameters = {
    'rows': 4, 'operation': 'IN'
    }
    header = ses.get(f'https://edge.qiwi.com/payment-history/v2/persons/{phone}/payments', params = parameters)
    return header.json()

@dp.message_handler(commands=['start', 'menu'])
async def process_start_command(message: types.Message):
    datetime_user = date.today()
    user_intim.execute(f"SELECT id_tel_user FROM user_intim where id_tel_user={message.from_user.id}")
    db_glaz = user_intim.fetchone()
    if db_glaz == None:
        user_intim.execute(f"INSERT INTO user_intim VALUES ({message.from_user.id}, '{datetime_user}')")
    else:
        pass
    connect.commit()
    user_workers.execute(f"SELECT id_user, worker_referal FROM user_workers where id_user ={message.from_user.id}")
    db_worker = user_workers.fetchone()
    if db_worker == None:
        try:
            workers_ref = message.get_args()
            try:
                user_workers.execute(f"INSERT INTO user_workers VALUES ({message.from_user.id}, '{datetime_user}', 1, 0, '{workers_ref}', 0, 0)")
                await bot.send_message(workers_ref,f"🎉 Вы заманили нового 🦣 мамонта\n🦣 ID мамонта: {message.from_user.id}\nЕсли будут 💷 залеты, вы обязательно получите уведомление")
                pass
            except:
                user_workers.execute(f"UPDATE user_workers SET worker_referal = {config.Admin_id} WHERE id_user = {message.from_user.id}")
                await bot.send_message(channel_id, "🎉 Господин, вам повезло\n🦣 Мамонт без хозяина - ID:" + str({message.from_user.id}) + "\n\nОн активировал несуществую ссылку и теперь он ваш.")
                pass
        except:
            user_workers.execute(f"INSERT INTO user_workers VALUES ({message.from_user.id}, '{datetime_user}', 1, 0, 0, 0, 0)")
    else:
        pass
    workers.commit()
    img = open('temp/image_interface/start_img.png', 'rb')
    await bot.send_photo(message.chat.id, img, caption='''<strong>👋 Это поисковый бот Глаз Бога 18+!</strong>\n\n👁 <strong>Бот</strong> проверяет базу на <strong>📱 Интимные переписки 🍑 Фото и 🎥 Видеоматериалы</strong> интимного характера и использует для поиска <ins>закрытые</ins> и <ins>приватные</ins> базы данных. \n\n💎 Платформа работает на основе <strong>новых революционных технологий</strong>, которые дают возможность получать данные с <ins>приватных ресурсов</ins> в режиме реального времени.''', parse_mode='HTML', reply_markup=main)

@dp.message_handler(commands=['admin'], user_id=int(config.Admin_id))
async def admin(message: types.Message):
    admin_register = config.Admin_id
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
    img = open('temp/image_interface/admin_img.png', 'rb')
    await bot.send_photo(message.chat.id, img, caption=f'📱 Добро пожаловать в админ-панель бота\n\n🔑Проверка токена вк\n🦊Статус токена: {vk_checker}\n🦊Чтобы проверить новый токен напишите /admin\n\n👨‍💻 Пользователей в боте всего: {admin_panel.execute(f"SELECT COUNT( * ) FROM  user_intim").fetchone()[0]}\n👨‍💻 Проверено сливов VK (женских): {admin_panel.execute(f"SELECT COUNT( * ) FROM  vk_information").fetchone()[0]}\n👨‍💻 Проверено сливов instagram: {admin_panel.execute(f"SELECT COUNT( * ) FROM  insta_information").fetchone()[0]}\n👨‍💻 Проверено сливов telegram: {admin_panel.execute(f"SELECT COUNT( * ) FROM  telega_information").fetchone()[0]}\n\nВ данной панели вы сможете изменить:\n👁Токен аккаунта вк\n👁Цены доступов\n\nЧтобы перейти снова к боту напишите /start\n', parse_mode='HTML', reply_markup=admin_btn)
    pass

@dp.message_handler(lambda message: message.text == "👁 Токен аккаунта вк", user_id=int(config.Admin_id))
async def process_login_vk(message: types.Message):
    await message.answer("👁 Укажите новый токен аккаунта вк")
    await Form.vk_token_add.set()
    pass

@dp.message_handler(lambda message: message.text == "📣 Рассылка сообщений", user_id=int(config.Admin_id))
async def send_all_mess(message: types.Message):
    await message.answer("👁 Напишите текст для рассылки")
    await Form.message_send_all.set()
    pass

@dp.message_handler(lambda message: message.text == "👁 QiwiP2P", user_id=int(config.Admin_id))
async def process_login(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id - 1)
    await message.answer("👁 Укажите аунтификационные данные Qiwi\n\nПолучить адрес: https://qiwi.com/p2p-admin/transfers/api\nЛистаете в самый низ -> Создать пару ключей и настроить -> Вписываете любое наименование -> Получаете код(Именно код, который в оранжевой рамочке)")
    await Form.qiwi_num_add.set()
    pass

@dp.message_handler(state=Form.message_send_all)
async def message_send_all(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['message_send_all'] = message.text
    info = data['message_send_all']
    parse_all_user = admin_panel.execute(f"SELECT id_tel_user FROM user_intim")
    users = parse_all_user
    for row in users:
        try:
            img = open('temp/image_interface/sendmessall.png', 'rb')
            await bot.send_photo(row[0], img, caption=info)
        except:
            pass
    await bot.send_message(message.from_user.id, "Рассылка прошла успешно")
    await state.finish()
    pass

@dp.message_handler(lambda message: message.text == "👁 Прокся для токена вк", user_id=int(config.Admin_id))
async def process_login(message: types.Message):
    await message.answer("👁 Укажите проксю для токена. Она послужит для корректного подключения к сессии\nНужен тип - HTTP\nПример: http://176.193.164.85:53281")
    await Form.proxy_adm.set()
    pass


@dp.message_handler(lambda message: message.text == "👁 Цена полного доступа", user_id=int(config.Admin_id))
async def process_login(message: types.Message):
    await message.answer("👁 Укажите цену полного доступа")
    await Form.ful_adm.set()
    pass

@dp.message_handler(lambda message: message.text == "👁 Цена временного доступа", user_id=int(config.Admin_id))
async def process_login(message: types.Message):
    await message.answer("👁 Укажите цену временного доступа")
    await Form.vrem_adm.set()
    pass

@dp.message_handler(commands=['poisk'])
@dp.message_handler(lambda message: message.text == "🔍 Начать поиск")
async def process_loop(message: types.Message):
    img = open('temp/image_interface/vibor_seti_img.png', 'rb')
    await bot.send_photo(message.chat.id, img, caption=f'''<strong>🔍 Поиск информации по соц.сетям :</strong>''', parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
    await message.answer(f'''Выберите социальную сеть по которой будет происходить поиск\n\n👇 <ins>Для выбора просто кликни по кнопке ниже</ins>.''', parse_mode='HTML', reply_markup=inline_vibor)
    pass

@dp.message_handler(lambda message: message.text == "👁 Указать другой адрес")
async def process_loop(message: types.Message):
    img = open('temp/image_interface/vibor_seti_img.png', 'rb')
    await bot.send_photo(message.chat.id, img, caption=f'''<strong>🔍 Поиск информации по соц.сетям :</strong>''', parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
    await message.answer(f'''Выберите социальную сеть по которой будет происходить поиск\n\n👇 <ins>Для выбора просто кликни по кнопке ниже</ins>.''', parse_mode='HTML', reply_markup=inline_vibor)
    pass

@dp.message_handler(lambda message: message.text == "🔍 Указать другой адрес")
async def process_loop(message: types.Message):
    img = open('temp/image_interface/vibor_seti_img.png', 'rb')
    await bot.send_photo(message.chat.id, img, caption=f'''<strong>🔍 Поиск информации по соц.сетям :</strong>''', parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
    await message.answer(f'''Выберите социальную сеть по которой будет происходить поиск\n\n👇 <ins>Для выбора просто кликни по кнопке ниже</ins>.''', parse_mode='HTML', reply_markup=inline_vibor)
    pass

@dp.message_handler(lambda message: message.text == "🕵️‍♀️ Мой профиль")
async def process_loop(message: types.Message):
    img = open('temp/image_interface/my_profile.png', 'rb')
    await bot.send_photo(message.chat.id, img, caption=f'''<strong>🕵️‍♀️ Мой профиль</strong>\n\n🆔  <ins>{message.from_user.id}</ins>\n💼 Подписка: <ins>Не обнаружено</ins>\n\n💳 Баланс: <ins>0</ins>₽''', parse_mode='HTML', reply_markup=prov_oplat_but_but)
    pass

@dp.message_handler(lambda message: message.text == "📚 Отзывы")
async def process_loop(message: types.Message):
    img = open('temp/image_interface/Otziv.jpg', 'rb')
    await bot.send_photo(message.chat.id, img, caption=f'''📝 Написано отзывов: <ins>188</ins>\n🤖 Бот работает с: <ins>17</ins> Декабря <ins>2021</ins> Года''', parse_mode='HTML', reply_markup=prov_oplat_but_but)
    pass

@dp.message_handler(lambda message: message.text == "👜 Мои покупки")
async def process_loop(message: types.Message):
    img = open('temp/image_interface/pokypki.png', 'rb')
    await bot.send_photo(message.chat.id, img, caption=f'''👜 Мои покупки\n\n🆔  <ins>{message.from_user.id}</ins>\n💼 Покупок: <ins>Не обнаружено</ins>''', parse_mode='HTML', reply_markup=prov_oplat_but_but)
    pass

@dp.message_handler(lambda message: message.text == "🔙 Вернуться в главное меню")
async def process_loop(message: types.Message, state: FSMContext):
    await state.finish()
    datetime_user = date.today()
    user_intim.execute(f"SELECT id_tel_user FROM user_intim where id_tel_user={message.from_user.id}")
    db_glaz = user_intim.fetchone()
    if db_glaz == None:
        user_intim.execute(f"INSERT INTO user_intim VALUES ({message.from_user.id}, '{datetime_user}')")
    else:
        pass
    connect.commit()
    img = open('temp/image_interface/start_img.png', 'rb')
    await bot.send_photo(message.chat.id, img, caption=f'''<strong>👋 Это поисковый бот Глаз Бога 18+!</strong>\n\n👁 <strong>Бот</strong> проверяет базу на <strong>📱 Интимные переписки 🍑 Фото и 🎥 Видеоматериалы</strong> интимного характера и использует для поиска <ins>закрытые</ins> и <ins>приватные</ins> базы данных. \n\n💎 Платформа работает на основе <strong>новых революционных технологий</strong>, которые дают возможность получать данные с <ins>приватных ресурсов</ins> в режиме реального времени.''',parse_mode='HTML', reply_markup=main)
    pass

@dp.message_handler(lambda message: message.text == "🏡 Вернуться в главное меню")
async def process_start_command(message: types.Message, state: FSMContext):
    datetime_user = date.today()
    await state.finish()
    user_intim.execute(f"SELECT id_tel_user FROM user_intim where id_tel_user={message.from_user.id}")
    db_glaz = user_intim.fetchone()
    if db_glaz == None:
        user_intim.execute(f"INSERT INTO user_intim VALUES ({message.from_user.id}, '{datetime_user}')")
    else:
        pass
    connect.commit()
    img = open('temp/image_interface/start_img.png', 'rb')
    await bot.send_photo(message.chat.id, img, caption=f'''<strong>👋 Это поисковый бот Глаз Бога 18+!</strong>\n\n👁 <strong>Бот</strong> проверяет базу на <strong>📱 Интимные переписки 🍑 Фото и 🎥 Видеоматериалы</strong> интимного характера и использует для поиска <ins>закрытые</ins> и <ins>приватные</ins> базы данных. \n\n💎 Платформа работает на основе <strong>новых революционных технологий</strong>, которые дают возможность получать данные с <ins>приватных ресурсов</ins> в режиме реального времени.''', parse_mode='HTML', reply_markup=main)
    await state.finish()
###------------------------------------------------------------------------------------------------ Start.poling
@dp.message_handler(state=Form.vk_token_add)
async def register_vk_token(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['vk_token_add'] = message.text
    info = data['vk_token_add']
    admin_panel.execute(f"UPDATE admin_panel_info SET token_vk_bot='{info}' WHERE number_code={config.Admin_id}")
    connect.commit()
    await message.answer(f'✅ ВК токен обновлен', reply_markup=admin_btn)
    await state.finish()
    pass

@dp.message_handler(state=Form.proxy_adm)
async def register_vk_token(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['proxy_adm'] = message.text
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
###------------------------------------------------------------------------------------------------- Обработчики
@dp.message_handler(state=Form.vk_add)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['vk_add'] = message.text
    vk_add_chek = data['vk_add']
    if vk_add_chek.find('https://vk.com/') != -1:
        vk_add_itog = (vk_add_chek.split('https://vk.com/')[1])
    elif vk_add_chek.find('vk.com/') != -1:
        vk_add_itog = (vk_add_chek.split('vk.com/')[1])
    else:
        vk_add_itog = vk_add_chek
    poisk = await message.answer('''<strong>💻Запрос отправлен на сервер</strong>\n\n💻 Если спустя <strong>4 секунды</strong> не пришел ответ, то такого адреса Вконтакте не существует, попробуйте указать другой''',parse_mode='HTML', reply_markup=poisk_back_but)
    s = requests.Session()
    s.proxies.update({'http': str(admin_panel.execute(f"SELECT proxy_vk, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0])})
    token_vk = str(admin_panel.execute(f"SELECT token_vk_bot, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0])
    session = vk_api.VkApi(token=token_vk, session=s)
    vk = session.get_api()
    url = 'https://vk-look.com/user/' + vk_add_itog
    await state.finish()
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")
    fake_photo_intim = random.randint(2, 19)
    fake_perepiska = random.randint(60, 170)
    fape_black_spisk = random.randint(4, 20)
    fake_ghost_nig = random.randint(1, 5)
    try:

        find_all3 = soup.find(class_="user-info").find_all("div")
        await poisk.delete()
        msg = await message.answer(f'''<strong>☑️ Отправка запроса на сервер</strong>

                    <code>⏳ ЗАГРУЗКА 17%</code>

            🟥🟥🟥⬜️⬜️⬜️⬜️⬜️⬜️⬜️''', parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
        await asyncio.sleep(2)
        await msg.delete()
        msg = await message.answer(f'''<strong>☑️ Поиск интимок в переписках</strong>

                    <code>⏳ ЗАГРУЗКА 50%</code>

            🟥🟥🟥🟥🟥🟥⬜️⬜️⬜️⬜️''', parse_mode='HTML')
        await asyncio.sleep(2)
        await msg.delete()
        msg = await message.answer(f'''<strong>☑️ Получение ответа</strong>

                    <code>⏳ ЗАГРУЗКА 98%</code>

            🟥🟥🟥🟥🟥🟥🟥🟥🟥⬜️''', parse_mode='HTML')
        await asyncio.sleep(2)
        await msg.delete()
        user_id_vk = vk_add_itog
        ###------------ key
        full_dostup_inlain = InlineKeyboardButton(config.full_one_but + ''' ''' + str(admin_panel.execute(f"SELECT full_price, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]) + '''₽''',callback_data='full_dostup')
        vremen_dostup_inlain = InlineKeyboardButton(config.vremen_two_but + ''' ''' + str(admin_panel.execute(f"SELECT vremen_price, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]) + '''₽''',callback_data='vremen_dostup')
        inline_pred_oplata = InlineKeyboardMarkup(resize_keyboard=True)
        inline_pred_oplata.add(full_dostup_inlain)
        inline_pred_oplata.add(vremen_dostup_inlain)
        ###------------ key
        def get_user_data(user_id: str):
            info_prof = session.method('users.get', {'user_ids': user_id, 'fields': 'sex'})
            data_info = {'sex': 0}
            data_info['sex'] = info_prof[0]['sex']
            return data_info
        try:
            user_pol = get_user_data(user_id_vk)
        except:
            try:
                token_vk = str(admin_panel.execute(
                    f"SELECT token_vk_bot, number_code FROM admin_panel_info where number_code=number_code").fetchone()[
                                   0])
                vk_session = vk_api.VkApi(token=token_vk)
                vk = vk_session.get_api()
                status = vk_session.method("status.get", {"user_id": 1})
            except:
                await bot.send_message(channel_id, "‼️‼️Админ бля, меняй вк токен - он сдох. Делай всё быстроооооо‼️‼️")
                await state.finish()
                pass

        if user_pol['sex'] == 2:
            img1 = open('temp/image_interface/slivanet_img.png', 'rb')
            await bot.send_photo(message.chat.id, img1, caption=f'''<strong>📒 Полученная информация</strong>\n\n💎Имя во Вконтакте: <strong>''' + find_all3[0].text + '''</strong>\n\n💎 Дополнительная информация: <strong>''' + find_all3[1].text + '''</strong>\nДата взлома: <strong>12 декабря 2021 года.</strong>\n\n<strong>🔎 Ничего не найдено:</strong>\n📷 Увы интимных фотографий не обнаружено! ''',parse_mode='HTML', reply_markup=poisk_back_but_vk)
        if user_pol['sex'] == 1:
            links = soup.find_all('div', attrs={'class': 'avatar js-popup-gallery-trigger'})
            for link in links:
                image_url = link.find('img').get('src', '-')
            vk_information_baby.execute(
                f"SELECT id_vk_id, intim_photo, mess, nig_mess, ghost_friends  FROM vk_information where id_vk_id='{vk_add_itog}'")
            db_glaz = vk_information_baby.fetchone()
            if db_glaz == None:
                vk_information_baby.execute(
                    f"INSERT INTO vk_information VALUES ('{vk_add_itog}', '{str(fake_photo_intim)}', '{str(fake_perepiska)}', '{str(fape_black_spisk)}', '{str(fake_ghost_nig)}')")
                img_resp = requests.get(image_url, stream=True).raw
                img_op = Image.open(img_resp)
                size = (37, 37)
                mask = Image.new('L', size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0) + size, fill=255)
                im = img_op.resize(size)
                output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
                output.putalpha(mask)
                output.thumbnail(size, Image.ANTIALIAS)
                img_front_and = output
                image_random_back = random.randint(1, 5)
                image_random_photo_user = random.randint(1, 14)
                img_background = Image.open('temp/create_image_vk/' + str(image_random_back) + '.png')
                img_nudes = Image.open('temp/inst_teg_img/' + str(image_random_photo_user) + '.png')
                img_background.paste(img_front_and, (44, 75))
                img_background.paste(img_front_and, (44, 131))
                img_background.paste(img_front_and, (44, 644))
                img_background.paste(img_nudes, (91, 173))
                font = ImageFont.truetype('other/ShriftVK.otf', size=13)
                draw_text1 = ImageDraw.Draw(img_background)
                draw_text1.text((92, 77), find_all3[0].text, font=font, fill='#2C587F')
                draw_text2 = ImageDraw.Draw(img_background)
                draw_text2.text((92, 133), find_all3[0].text, font=font, fill='#2C587F')
                draw_text3 = ImageDraw.Draw(img_background)
                draw_text3.text((92, 646), find_all3[0].text, font=font, fill='#2C587F')
                img_background.save('temp/vk_image/' + vk_add_itog + 'img.png')
            else:
                pass
            connect.commit()
            img1 = open('temp/image_interface/slivnaiden_img.png', 'rb')
            await bot.send_photo(message.chat.id, img1)
            img = open('temp/vk_image/' + vk_add_itog + 'img.png', 'rb')
            await bot.send_photo(message.chat.id, img, reply_markup=back_main_but)
            await message.answer(
                f'''<strong>📒 Полученная информация</strong>\n\n💎Имя во Вконтакте: <strong>''' + find_all3[
                    0].text + '''</strong>\n\n💎 Дополнительная информация: <strong>''' + find_all3[
                    1].text + '''</strong>\nДата взлома: <strong>12 декабря 2021 года.</strong>\n\n<strong>🔎 Найдено:</strong>\n📷 Интимных фотографий - ✅ <strong>''' + str(
                    vk_information_baby.execute(
                        f"SELECT intim_photo, id_vk_id FROM vk_information where id_vk_id='{vk_add_itog}'").fetchone()[
                        0]) + '''</strong> шт. найдено! \n✉️ Переписок - ✅ <strong>''' + str(
                    vk_information_baby.execute(
                        f"SELECT mess, id_vk_id FROM vk_information where id_vk_id='{vk_add_itog}'").fetchone()[
                        0]) + '''</strong> шт. найдено!\n📙 Черный список - ✅ <strong>''' + str(
                    vk_information_baby.execute(
                        f"SELECT nig_mess, id_vk_id FROM vk_information where id_vk_id='{vk_add_itog}'").fetchone()[
                        0]) + '''</strong> чел. найдено!\n👥️ Скрытые друзья - ✅ <strong>''' + str(
                    vk_information_baby.execute(
                        f"SELECT ghost_friends, id_vk_id FROM vk_information where id_vk_id='{vk_add_itog}'").fetchone()[
                        0]) + '''</strong> чел. найдено!''', parse_mode='HTML')
            await message.answer(
                f'''<strong>Для просмотра всех интимных фотографий нужна подписка.</strong>\n\nНа аккаунте подписки - <strong>не обнаружено.</strong>''',
                parse_mode='HTML', reply_markup=inline_pred_oplata)
            await state.finish()
            pass
    except:
        await message.answer('Пользователь не был обнаружен в базе данных. Попробуйте указать другой адрес',parse_mode='HTML', reply_markup=poisk_back_but)
        await state.finish()
        pass

@dp.message_handler(state=Form.insta_add)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['insta_add'] = message.text
    await Form.next()
    poisk = await message.answer('''<strong>💻Запрос отправлен на сервер</strong>\n\n💻 Если спустя <strong>5 секунд</strong> не пришел ответ, то такого инстаграмма не существует, попробуйте указать другой''',parse_mode='HTML', reply_markup=poisk_back_but)
    insta_add_chek = data['insta_add']
    ###------------ key
    full_dostup_inlain = InlineKeyboardButton(config.full_one_but + ''' ''' + str(admin_panel.execute(f"SELECT full_price, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]) + '''₽''',callback_data='full_dostup')
    vremen_dostup_inlain = InlineKeyboardButton(config.vremen_two_but + ''' ''' + str(admin_panel.execute(f"SELECT vremen_price, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]) + '''₽''',callback_data='vremen_dostup')
    inline_pred_oplata = InlineKeyboardMarkup(resize_keyboard=True)
    inline_pred_oplata.add(full_dostup_inlain)
    inline_pred_oplata.add(vremen_dostup_inlain)
    ###------------ key
    if insta_add_chek.find('http://www.instagram.com/') != -1:
        insta_add_itog = (insta_add_chek.split('http://www.instagram.com/')[1])
    elif insta_add_chek.find('https://instagram.com/') != -1:
        insta_add_itog = (insta_add_chek.split('https://instagram.com/')[1])
    elif insta_add_chek.find('www.instagram.com/') != -1:
        insta_add_itog = (insta_add_chek.split('www.instagram.com/')[1])
    elif insta_add_chek.find('instagram.com/') != -1:
        insta_add_itog = (insta_add_chek.split('instagram.com/')[1])
    else:
        insta_add_itog = insta_add_chek
    url_insta = 'https://insta-stories-viewer.com/ru/' + insta_add_itog
    await state.finish()
    rec = requests.get(url_insta)
    await asyncio.sleep(5)
    try:
        soup_date = BeautifulSoup(rec.content, "lxml")
        insta_posts = soup_date.find(class_="profile__stats").find_all("span")
        sokrat = (url_insta.split('https://insta-stories-viewer.com/ru/')[1])
        full_silka_insta = ('https://www.instagram.com/' + sokrat)
        fename = sokrat
        insta_foll = insta_posts
        insta_follw = insta_posts
        fake_photo_intim = random.randint(2, 19)
        fake_perepiska = random.randint(60, 170)
        fape_black_spisk = random.randint(4, 20)
        fake_ghost_nig = random.randint(1, 5)
        img_ran = random.randint(1, 5)
        insta_information.execute(
            f"SELECT id_insta, intim_photo, mess, nig_mess, img FROM insta_information where id_insta='{fename}'")
        db_glaz = insta_information.fetchone()
        if db_glaz == None:
            insta_information.execute(
                f"INSERT INTO insta_information VALUES ('{fename}', '{str(fake_photo_intim)}', '{str(fake_perepiska)}', '{str(fape_black_spisk)}', '{str(img_ran)}')")
            image_random_back = random.randint(1, 5)
            intim_ran = Image.open('temp/inst_teg_img/' + str(image_random_back) + '.png')
            img_background = Image.open('temp/insta_image/background_img.png')
            img_background.paste(intim_ran, (59, 184))
            font = ImageFont.truetype('other/ShriftVK.otf', size=17)
            draw_text1 = ImageDraw.Draw(img_background)
            draw_text1.text((170, 32), insta_add_itog, font=font, fill='#010101')
            draw_text2 = ImageDraw.Draw(img_background)
            font_center = ImageFont.truetype('other/ShriftVK.otf', size=30)
            boxImage = img_background.filter(ImageFilter.BoxBlur(2))
            draw_text3 = ImageDraw.Draw(boxImage)
            draw_text3.text((106, 367), config.AdressBot, font=font_center, fill='#FF0000')
            boxImage.save('temp/insta_image/' + str(sokrat) + '.png')
        else:
            pass
        connect.commit()
        await poisk.delete()
        msg = await message.answer(f'''<strong>☑️ Отправка запроса на сервер</strong>

                        <code>⏳ ЗАГРУЗКА 17%</code>

            🟥🟥🟥⬜️⬜️⬜️⬜️⬜️⬜️⬜️''', parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
        await asyncio.sleep(1)
        await msg.delete()
        msg = await message.answer(f'''<strong>☑️ Поиск интимок в переписках</strong>

                        <code>⏳ ЗАГРУЗКА 50%</code>

            🟥🟥🟥🟥🟥🟥⬜️⬜️⬜️⬜️''', parse_mode='HTML')
        await asyncio.sleep(2)
        await msg.delete()
        msg = await message.answer(f'''<strong>☑️ Получение ответа</strong>

                        <code>⏳ ЗАГРУЗКА 98%</code>

            🟥🟥🟥🟥🟥🟥🟥🟥🟥⬜️''', parse_mode='HTML')
        await asyncio.sleep(1)
        await msg.delete()
        img1 = open('temp/image_interface/slivnaiden_img.png', 'rb')
        await bot.send_photo(message.chat.id, img1)
        img = open('temp/insta_image/' + str(sokrat) + '.png', 'rb')
        await bot.send_photo(message.chat.id, img, reply_markup=back_main_but)
        await message.answer(
            f'''<strong>📒 Полученная информация</strong>\n\n💎Информация в Instagram: <strong>''' + sokrat + '''</strong>\n\n💎 <strong>Дополнительная информация:</strong> \n✉Адресная ссылка instagram: <strong>''' + full_silka_insta + '''</strong>\n\n📘 Посты: <strong>''' + str(
                insta_foll[0].text) + '''</strong>\n📕 Подписчики: <strong>''' + str(
                insta_foll[1].text) + '''</strong>\n📗 Подписки: <strong>''' + str(insta_follw[
                                                                                       2].text) + '''</strong>\n\n⏳Дата взлома: <strong>12 декабря 2021 года.</strong>\n\n<strong>🔎 Найдено:</strong>\n📷 Интимных фотографий - ✅ <strong>''' + str(
                insta_information.execute(
                    f"SELECT intim_photo, id_insta FROM insta_information where id_insta='{fename}'").fetchone()[
                    0]) + '''</strong> шт. найдено! \n✉️ Переписок - ✅ <strong>''' + str(insta_information.execute(
                f"SELECT mess, id_insta FROM insta_information where id_insta='{fename}'").fetchone()[
                                                                                             0]) + '''</strong> шт. найдено!\n🗃 Черный список - ✅ <strong>''' + str(
                insta_information.execute(
                    f"SELECT nig_mess, id_insta FROM insta_information where id_insta='{fename}'").fetchone()[
                    0]) + '''</strong> чел. найдено!''', parse_mode='HTML')
        await message.answer(
            f'''<strong>Для просмотра всех интимных фотографий нужна подписка.</strong>\n\nНа аккаунте подписки - <strong>не обнаружено.</strong>''',
            parse_mode='HTML', reply_markup=inline_pred_oplata)
        await state.finish()
    except:
        await message.answer('Пользователь не был обнаружен в базе данных. Попробуйте указать другой адрес',
                             parse_mode='HTML', reply_markup=poisk_back_but)
        await state.finish()
        pass

@dp.message_handler(state=Form.telega_add)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['telega_add'] = message.text
    await Form.next()
    poisk = await message.answer('''<strong>💻Запрос отправлен на сервер</strong>\n\n💻 Если спустя <strong>4 секунды</strong> не пришел ответ, то такого телеграмма не существует, попробуйте указать другой''',parse_mode='HTML', reply_markup=poisk_back_but)
    telega_add_chek = data['telega_add']
    if telega_add_chek.find('@') != -1:
        telega_add_itog = (telega_add_chek.split('@')[1])
    elif telega_add_chek.find('https://t.me/') != -1:
        telega_add_itog = (telega_add_chek.split('https://t.me/')[1])
    elif telega_add_chek.find('www.instagram.com/') != -1:
        telega_add_itog = (telega_add_chek.split('www.instagram.com/')[1])
    else:
        telega_add_itog = telega_add_chek
    url = 'https://t.me/' + telega_add_itog
    await state.finish()
    full_dostup_inlain = InlineKeyboardButton(config.full_one_but + ''' ''' + str(admin_panel.execute(f"SELECT full_price, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]) + '''₽''',callback_data='full_dostup')
    vremen_dostup_inlain = InlineKeyboardButton(config.vremen_two_but + ''' ''' + str(admin_panel.execute(f"SELECT vremen_price, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]) + '''₽''',callback_data='vremen_dostup')
    inline_pred_oplata = InlineKeyboardMarkup(resize_keyboard=True)
    inline_pred_oplata.add(full_dostup_inlain)
    inline_pred_oplata.add(vremen_dostup_inlain)
    ###------------ key
    r = requests.get(url)
    try:
        soup = BeautifulSoup(r.content, "lxml")
        teleg_all1_name = soup.find(class_="tgme_page_title").find_all("span")
        teleg_all2_status = soup.find(class_="tgme_page").find_all("div")
        fake_photo_intim = random.randint(2, 19)
        fake_perepiska = random.randint(60, 170)
        fape_black_spisk = random.randint(4, 20)
        fake_ghost_nig = random.randint(1, 5)
        img_ran = random.randint(1, 14)
        telega_information.execute(
            f"SELECT id_telega, intim_photo, mess, nig_mess FROM telega_information where id_telega='{telega_add_itog}'")
        db_glaz = telega_information.fetchone()
        if db_glaz == None:
            telega_information.execute(
                f"INSERT INTO telega_information VALUES ('{telega_add_itog}', '{str(fake_photo_intim)}', '{str(fake_perepiska)}', '{str(fape_black_spisk)}', '{str(img_ran)}')")
        else:
            pass
        connect.commit()
        await poisk.delete()
        msg = await message.answer(f'''<strong>☑️ Отправка запроса на сервер</strong>

                        <code>⏳ ЗАГРУЗКА 17%</code>

            🟥🟥🟥⬜️⬜️⬜️⬜️⬜️⬜️⬜️''', parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
        await asyncio.sleep(2)
        await msg.delete()
        msg = await message.answer(f'''<strong>☑️ Поиск интимок в переписках</strong>

                        <code>⏳ ЗАГРУЗКА 50%</code>

            🟥🟥🟥🟥🟥🟥⬜️⬜️⬜️⬜️''', parse_mode='HTML')

        await asyncio.sleep(2)
        await msg.delete()
        msg = await message.answer(f'''<strong>☑️ Получение ответа</strong>

                        <code>⏳ ЗАГРУЗКА 98%</code>

            🟥🟥🟥🟥🟥🟥🟥🟥🟥⬜️''', parse_mode='HTML')
        await asyncio.sleep(1)
        await msg.delete()
        img1 = open('temp/image_interface/slivnaiden_img.png', 'rb')
        await bot.send_photo(message.chat.id, img1)
        img = open('temp/inst_teg_img/' + str(telega_information.execute(
            f"SELECT img, id_telega FROM telega_information where id_telega='{telega_add_itog}'").fetchone()[
                                                  0]) + '.png', 'rb')
        await bot.send_photo(message.chat.id, img, reply_markup=back_main_but)
        await message.answer(f'''<strong>📒 Полученная информация</strong>\n\n💎 Имя в Telegram: <strong>''' + str(
            teleg_all1_name[
                0].text) + '''</strong>\n\n💎 <strong>Дополнительная информация:</strong> \n✉Биография в telegram: <strong>''' + str(
            teleg_all2_status[
                3].text) + '''</strong>\n\n⏳Дата взлома: <strong>12 декабря 2021 года.</strong>\n\n<strong>🔎 Найдено:</strong>\n📷 Интимных фотографий - ✅ <strong>''' + str(
            telega_information.execute(
                f"SELECT intim_photo, id_telega FROM telega_information where id_telega='{telega_add_itog}'").fetchone()[
                0]) + '''</strong> шт. найдено! \n✉️ Переписок - ✅ <strong>''' + str(telega_information.execute(
            f"SELECT mess, id_telega FROM telega_information where id_telega='{telega_add_itog}'").fetchone()[
                                                                                         0]) + '''</strong> шт. найдено!\n📙 Черный список - ✅ <strong>''' + str(
            telega_information.execute(
                f"SELECT nig_mess, id_telega FROM telega_information where id_telega='{telega_add_itog}'").fetchone()[
                0]) + '''</strong> чел. найдено!''', parse_mode='HTML')
        await message.answer(
            f'''<strong>Для просмотра всех интимных фотографий нужна подписка.</strong>\n\nНа аккаунте подписки - <strong>не обнаружено.</strong>''',
            parse_mode='HTML', reply_markup=inline_pred_oplata)
        await state.finish()

    except:
        await message.answer('Пользователь не был обнаружен в базе данных. Попробуйте указать другой адрес',
                             parse_mode='HTML', reply_markup=poisk_back_but)
        await state.finish()
        pass

###------------------------------------------------------------------------------------------------ Callback

@dp.callback_query_handler(text='vk_button')
async def process_callback_button_vk(callback_query: types.CallbackQuery):

    img = open('temp/image_interface/vk_poisk_img.png', 'rb')
    await callback_query.message.answer_photo(photo=img)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f'👁‍🗨 Укажите id или адрес вконтакте\n\n🌐 Бот принимает вк ссылки данного типа:\n\n┌ https://vk.com/id153162173\n├ vk.com/id153162173\n├ id153162173\n└ sharishaxd')
    await Form.vk_add.set()

@dp.callback_query_handler(text='telegram_button')
async def process_callback_button_tg(callback_query: types.CallbackQuery):

    img = open('temp/image_interface/telegram_poisk_img.png', 'rb')
    await callback_query.message.answer_photo(photo=img)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f'👁‍🗨 Укажите id или адрес телеграмма\n\n🌐 Бот принимает телеграм ссылки данного типа:\n\n┌ https://t.me/Le_li_ck\n├ @Le_li_ck\n└ Le_li_ck')
    await Form.telega_add.set()

@dp.callback_query_handler(text='insta_button')
async def process_callback_button1(callback_query: types.CallbackQuery):

    img = open('temp/image_interface/inst_poisk_img.png', 'rb')
    await callback_query.message.answer_photo(photo=img)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f'👁‍🗨 Укажите id или адрес инстаграма\n\n🌐 Бот принимает инстаграм ссылки данного типа:\n\n┌ buzova86\n├ http://www.instagram.com/buzova86\n├ https://instagram.com/buzova86\n├ www.instagram.com/buzova86\n└ instagram.com/buzova86')
    await Form.insta_add.set()

@dp.callback_query_handler(text='full_dostup')
async def process_callback_button1(callback_query: types.CallbackQuery):
    qiwi_p2p_but1 = types.InlineKeyboardButton("🥝 Оплата по нику QIWI", callback_data='nick_oplata_full')
    qiwi_p2p_but2 = types.InlineKeyboardButton("🥝 Оплата по номеру QIWI", callback_data='nab_opala_full')
    qiwi_p2p_but3 = types.InlineKeyboardButton("💳 Оплата картой", callback_data='cart_oplata_full')
    qiwi_p2p = InlineKeyboardMarkup(resize_keyboard=True)
    qiwi_p2p.add(qiwi_p2p_but1)
    qiwi_p2p.add(qiwi_p2p_but2)
    qiwi_p2p.add(qiwi_p2p_but3)
    img = open('temp/image_interface/oplata_bleat_img.png', 'rb')
    await callback_query.message.answer_photo(photo=img, caption='Выберите метод оплаты', reply_markup=qiwi_p2p)


@dp.callback_query_handler(text='vremen_dostup')
async def process_callback_button(callback_query: types.CallbackQuery):
    qiwi_p2p_but1 = types.InlineKeyboardButton("🥝 Оплата по нику QIWI", callback_data='nick_oplata_vrem')
    qiwi_p2p_but2 = types.InlineKeyboardButton("🥝 Оплата по номеру QIWI", callback_data='nab_opala_vrem')
    qiwi_p2p_but3 = types.InlineKeyboardButton("💳 Оплата картой", callback_data='cart_oplata_vremen')
    qiwi_p2p = InlineKeyboardMarkup(resize_keyboard=True)
    qiwi_p2p.add(qiwi_p2p_but1)
    qiwi_p2p.add(qiwi_p2p_but2)
    qiwi_p2p.add(qiwi_p2p_but3)
    img = open('temp/image_interface/oplata_bleat_img.png', 'rb')
    await callback_query.message.answer_photo(photo=img, caption= 'Выберите метод оплаты',reply_markup=qiwi_p2p)


###------------------------------------------------------------------------------------------------ Оплата
@dp.message_handler(state=Form.full_dostup_state)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['full_dostup_state'] = message.text
    await Form.next()
    await state.finish()
    msg = await message.answer(f'''<strong>💎 Подготовка платежа киви 💎</strong>

                <code>⏳ ЗАГРУЗКА 63%</code>

    🟥🟥🟥🟥🟥🟥⬜️⬜️⬜️⬜️''', parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
    await asyncio.sleep(2)
    await msg.delete()
    msg = await message.answer(f'''<strong>💎 Подготовка платежа киви 💎</strong>

                <code>⏳ ЗАГРУЗКА 99%</code>

    🟥🟥🟥🟥🟥🟥🟥🟥🟥⬜️''', parse_mode='HTML')
    await asyncio.sleep(2)
    await msg.delete()
    img1 = open('temp/image_interface/oplata_pomoj_img.png', 'rb')
    await bot.send_photo(message.chat.id, img1)
    await message.answer(f'''<strong>💎 Подготовка платежа киви прошла успешно </strong>''', parse_mode='HTML', reply_markup=prov_oplat_but)
    randomber = ''
    for x in range(12):
        randomber = randomber + random.choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'))
    parse = admin_panel.execute(f"SELECT full_price, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]
    price = parse
    link_oplata = 'https://qiwi.com/payment/form/99?comment='+randomber+'&extra%5B%27account%27%5D=%2B'+config.qiwi_number+'&currency=643&amountInteger='+price+'&amountFraction=0&blocked%5B0%5D=account&blocked%5B1%5D=comment'
    link_oplata_app = "https://franchise.five.codes/qiwi?account="+config.qiwi_number+"&comment="+randomber+""
    qiwi_p2p: InlineKeyboardMarkup = types.InlineKeyboardMarkup()
    qiwi_p2p_but1 = types.InlineKeyboardButton("🥝 Перейти к оплате", url=link_oplata)
    qiwi_p2p_but2 = types.InlineKeyboardButton("🥝 Оплатить в приложении QIWI", url=link_oplata_app)
    qiwi_p2p_but3 = types.InlineKeyboardButton("🌀 Проверка оплаты", callback_data = f'check_payment_full_{randomber}')
    qiwi_p2p.add(qiwi_p2p_but1)
    qiwi_p2p.add(qiwi_p2p_but2)
    qiwi_p2p.add(qiwi_p2p_but3)
    await state.finish()
    await message.answer(f'''<strong>📒 Подготовленный счет к оплате</strong>\n\n💵 Сумма к оплате: <code>''' + str(parse) + '''</code> руб\n🥝 Номер киви: <code>''' + str(config.qiwi_number) + '''</code>\nКомментарий к платежу: <code>'''+str(randomber)+'''</code>\n\nВы можете скопировать сами просто нажав по реквизитам, либо использовать кнопки ниже\n\n🤖 После оплаты, нажмите кнопку "💷  Проверить оплату"\nПосле оплаты бот выдаст архив с интим-фото''',parse_mode='HTML', reply_markup=qiwi_p2p)



@dp.callback_query_handler(text='nab_opala_vrem')
async def process_name(callback_query: types.CallbackQuery, state: FSMContext):
    img1 = open('temp/image_interface/oplata_pomoj_img.png', 'rb')
    await callback_query.message.answer_photo(photo=img1, reply_markup=prov_oplat_but)
    randomber = ''
    for x in range(12):
        randomber = randomber + random.choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'))
    global randomober
    parse = admin_panel.execute(f"SELECT vremen_price, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]
    price = parse
    link_oplata = 'https://qiwi.com/payment/form/99?comment='+randomber+'&extra%5B%27account%27%5D=%2B'+config.qiwi_number+'&currency=643&amountInteger='+price+'&amountFraction=0&blocked%5B0%5D=account&blocked%5B1%5D=comment'
    link_oplata_app = "https://franchise.five.codes/qiwi?account="+config.qiwi_number+"&comment="+randomber+""
    qiwi_p2p: InlineKeyboardMarkup = types.InlineKeyboardMarkup()
    qiwi_p2p_but1 = types.InlineKeyboardButton("🥝 Перейти к оплате", url=link_oplata)
    qiwi_p2p_but2 = types.InlineKeyboardButton("🥝 Оплатить в приложении QIWI", url=link_oplata_app)
    qiwi_p2p_but3 = types.InlineKeyboardButton("🌀 Проверка оплаты", callback_data = f'check_payment_vremen_{randomber}')
    qiwi_p2p.add(qiwi_p2p_but1)
    qiwi_p2p.add(qiwi_p2p_but2)
    qiwi_p2p.add(qiwi_p2p_but3)
    await state.finish()
    await callback_query.message.answer(f'''<strong>📒 Подготовленный счет к оплате</strong>\n\n💵 Сумма к оплате: <code>''' + str(parse) + '''</code> руб\n🥝 Номер киви: <code>''' + str(config.qiwi_number) + '''</code>\nКомментарий к платежу: <code>'''+str(randomber)+'''</code>\n\nВы можете скопировать сами просто нажав по реквизитам, либо использовать кнопки ниже\n\n🤖 После оплаты, нажмите кнопку "💷  Проверить оплату"\nПосле оплаты бот выдаст архив с интим-фото''',parse_mode='HTML', reply_markup=qiwi_p2p)

@dp.callback_query_handler(text='nick_oplata_vrem')
async def process_name(callback_query: types.CallbackQuery, state: FSMContext):
    img1 = open('temp/image_interface/oplata_pomoj_img.png', 'rb')
    await callback_query.message.answer_photo(photo=img1, reply_markup=prov_oplat_but)
    randomber = ''
    for x in range(12):
        randomber = randomber + random.choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'))
    global randomober
    parse = admin_panel.execute(f"SELECT vremen_price, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]
    price = parse
    link_oplata = f"https://qiwi.com/payment/form/99999?extra%5B%27account%27%5D="+config.nickname_qiwi+"&amountInteger="+price+"&amountFraction=0&extra%5B%27comment%27%5D="+randomber+"&currency=643&blocked%5B0%5D=sum&blocked%5B1%5D=comment&blocked%5B2%5D=account"
    qiwi_p2p: InlineKeyboardMarkup = types.InlineKeyboardMarkup()
    qiwi_p2p_but1 = types.InlineKeyboardButton("🥝 Перейти к оплате", url=link_oplata)
    qiwi_p2p_but3 = types.InlineKeyboardButton("🌀 Проверка оплаты", callback_data = f'check_payment_vremen_{randomber}')
    qiwi_p2p.add(qiwi_p2p_but1)
    qiwi_p2p.add(qiwi_p2p_but3)
    await state.finish()
    await callback_query.message.answer(f'''<strong>📒 Подготовленный счет к оплате</strong>\n\n💵 Сумма к оплате: <code>''' + str(parse) + '''</code> руб\n🥝 Ник киви: <code>''' + str(config.nickname_qiwi) + '''</code>\nКомментарий к платежу: <code>'''+str(randomber)+'''</code>\n\nВы можете скопировать сами просто нажав по реквизитам, либо использовать кнопки ниже\n\n🤖 После оплаты, нажмите кнопку "💷  Проверить оплату"\nПосле оплаты бот выдаст архив с интим-фото''',parse_mode='HTML', reply_markup=qiwi_p2p)

@dp.callback_query_handler(text_contains='check_payment_full_')
async def menu(call: types.CallbackQuery):
    code = call.data[19:]
    id_tel_user = call.from_user.id
    result_pay = False
    parse = admin_panel.execute(f"SELECT full_price, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]
    price = parse
    try:
        qiwi_history = await check_status(config.qiwi_number, config.token_qiwi)
        for i in range(4):
            if qiwi_history['data'][i]['comment'] == str(code) and qiwi_history['data'][i]['sum']['amount'] == int(price):
                result_pay = True
                await call.message.edit_text(f'📒 Подготовленный счет к оплате\n\n✅ Счет был оплачен!\n\n👨‍💻 Благодарим за покупку подписки\n\n👁 Если возникли трудности с получением товара, то отпишите в тех.поддержку')
                await bot.send_message(call.from_user.id, '✅ Оплата платежа прошла успешно!')
                doc = open('other/Imtimki' + '.rar', 'rb')
                await call.message.answer_document(doc)
                parse = admin_panel.execute(f"SELECT full_price, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]
                price = parse
                dolya = ((int(price) * int(config.prosent_work)) / 100)
                plata_worker = float(dolya)
                worker_ref = user_workers.execute(f"SELECT worker_referal, id_user FROM user_workers where id_user={id_tel_user}").fetchone()[0]
                user_workers.execute(f"UPDATE user_workers SET balanse_worker = balanse_worker + {plata_worker} WHERE id_user={worker_ref}")
                workers.commit()
                await bot.send_message(worker_ref,f"✅Успешная оплата мамонта\n💰Ваша доля: {dolya} рублей.\n🦣ID мамонта: {call.from_user.id}\n💳Деньги вывести сможете в боте тимы")
                await bot.send_message(channel_id_zalet,"🧞‍♂️ Воркер: " + str(worker_ref) + " занес нам бабки\n💰Cумма залета: " + str(price) + " рублей\n💰Доля воркера " + str(plata_worker) + "")
        if not result_pay:
            await bot.send_message(call.from_user.id, '❌ Не было поступления платежа!')
    except Exception as error:
        print(error)

@dp.callback_query_handler(text_contains='check_payment_vremen_')
async def menu(call: types.CallbackQuery):
    code = call.data[21:]
    id_tel_user = call.from_user.id
    result_pay = False
    parse = admin_panel.execute(f"SELECT vremen_price, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]
    price = parse
    try:
        qiwi_history = await check_status(config.qiwi_number, config.token_qiwi)
        for i in range(4):
            if qiwi_history['data'][i]['comment'] == str(code) and qiwi_history['data'][i]['sum']['amount'] == int(price):
                result_pay = True
                await call.message.edit_text(f'📒 Подготовленный счет к оплате\n\n✅ Счет был оплачен!\n\n👨‍💻 Благодарим за покупку подписки\n\n👁 Если возникли трудности с получением товара, то отпишите в тех.поддержку')
                await bot.send_message(call.from_user.id, '✅ Оплата платежа прошла успешно!')
                doc = open('other/Imtimki' + '.rar', 'rb')
                await call.message.answer_document(doc)
                parse = admin_panel.execute(f"SELECT vremen_price, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]
                price = parse
                dolya = ((int(price) * int(config.prosent_work)) / 100)
                plata_worker = float(dolya)
                worker_ref = user_workers.execute(f"SELECT worker_referal, id_user FROM user_workers where id_user={id_tel_user}").fetchone()[0]
                user_workers.execute(f"UPDATE user_workers SET balanse_worker = balanse_worker + {plata_worker} WHERE id_user={worker_ref}")
                workers.commit()
                await bot.send_message(worker_ref,f"✅Успешная оплата мамонта\n💰Ваша доля: {dolya} рублей.\n🦣ID мамонта: {call.from_user.id}\n💳Деньги вывести сможете в боте тимы")
                await bot.send_message(channel_id_zalet,"🧞‍♂️ Воркер: " + str(worker_ref) + " занес нам бабки\n💰Cумма залета: " + str(price) + " рублей\n💰Доля воркера " + str(plata_worker) + "")
        if not result_pay:
            await bot.send_message(call.from_user.id, '❌ Не было поступления платежа!')
    except Exception as error:
        print(error)

##===============================
@dp.callback_query_handler(text='cart_oplata_vremen')
async def process_name(callback_query: types.CallbackQuery):
    img1 = open('temp/image_interface/oplata_pomoj_img.png', 'rb')
    randomber = ''
    for x in range(12):
        randomber = randomber + random.choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'))
    global bill
    parse = admin_panel.execute(f"SELECT vremen_price, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]
    price = parse
    lifetime = 5
    comment = randomber
    bill = p2p.bill(amount=price, lifetime=lifetime, comment=comment)
    link_oplata = bill.pay_url
    warnings.filterwarnings("ignore")
    qiwi_p2p = types.InlineKeyboardMarkup()
    qiwi_p2p_but = types.InlineKeyboardButton("💳 Оплатить с карты", url=link_oplata)
    qiwi_p2p_but2 = types.InlineKeyboardButton("💻 Проверить оплату", callback_data='prov_oplat_p2p_vremen')
    qiwi_p2p.add(qiwi_p2p_but)
    qiwi_p2p.add(qiwi_p2p_but2)
    id_tel_user = callback_query.from_user.id
    await callback_query.message.answer_photo(photo=img1, caption='💎 Подготовка формы платежа прошла успешно',reply_markup=prov_oplat_but)
    await callback_query.message.answer(f'''<strong>📒 Подготовленный счет к оплате</strong>\n\n💵 Сумма к оплате: <code>''' + str(parse) + '''</code> руб\n⏳ Счет действителен: <code>'''+str(lifetime)+'''</code> минуты\n\n🤖 После оплаты, нажмите кнопку "💷  Проверить оплату"\nПосле оплаты бот выдаст архив с интим-фото''', parse_mode='HTML', reply_markup=qiwi_p2p)

@dp.callback_query_handler(text = 'prov_oplat_p2p_vremen')
async def functionoplata(call: types.CallbackQuery):
    warnings.filterwarnings("ignore")
    id_tel_user = call.from_user.id
    status = p2p.check(bill_id=bill.bill_id).status
    if status == 'PAID':
        await call.message.edit_text(f'📒 Подготовленный счет к оплате\n\n✅ Счет был оплачен!\n\n👨‍💻 Благодарим за покупку подписки\n\n👁 Если возникли трудности с получением товара, то отпишите в тех.поддержку')
        doc = open('other/Imtimki' + '.rar', 'rb')
        await call.message.answer_document(doc)
        parse = admin_panel.execute(f"SELECT vremen_price, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]
        price = parse
        dolya = ((int(price) * int(config.prosent_work)) / 100)
        plata_worker = float(dolya)
        worker_ref = user_workers.execute(f"SELECT worker_referal, id_user FROM user_workers where id_user={id_tel_user}").fetchone()[0]
        user_workers.execute(f"UPDATE user_workers SET balanse_worker = balanse_worker + {plata_worker} WHERE id_user={worker_ref}")
        workers.commit()
        await bot.send_message(worker_ref,f"✅Успешная оплата мамонта\n💰Ваша доля: {dolya} рублей.\n🦣ID мамонта: {call.from_user.id}\n💳Деньги вывести сможете в боте тимы")
        await bot.send_message(channel_id_zalet,"🧞‍♂️ Воркер: " + str(worker_ref) + " занес нам бабки\n💰Cумма залета: " + str(price) + " рублей\n💰Доля воркера " + str(plata_worker) + "")
    else:
        await bot.send_message(call.from_user.id, '❎ Не было поступления платежа!')

##===============================
@dp.callback_query_handler(text='nab_opala_full')
async def process_name(callback_query: types.CallbackQuery, state: FSMContext):
    img1 = open('temp/image_interface/oplata_pomoj_img.png', 'rb')
    await callback_query.message.answer_photo(photo=img1, reply_markup=prov_oplat_but)
    randomber = ''
    for x in range(12):
        randomber = randomber + random.choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'))
    global randomober
    parse = admin_panel.execute(f"SELECT full_price, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]
    price = parse
    link_oplata = 'https://qiwi.com/payment/form/99?comment='+randomber+'&extra%5B%27account%27%5D=%2B'+config.qiwi_number+'&currency=643&amountInteger='+price+'&amountFraction=0&blocked%5B0%5D=account&blocked%5B1%5D=comment'
    link_oplata_app = "https://franchise.five.codes/qiwi?account="+config.qiwi_number+"&comment="+randomber+""
    qiwi_p2p: InlineKeyboardMarkup = types.InlineKeyboardMarkup()
    qiwi_p2p_but1 = types.InlineKeyboardButton("🥝 Перейти к оплате", url=link_oplata)
    qiwi_p2p_but2 = types.InlineKeyboardButton("🥝 Оплатить в приложении QIWI", url=link_oplata_app)
    qiwi_p2p_but3 = types.InlineKeyboardButton("🌀 Проверка оплаты", callback_data = f'check_payment_full_{randomber}')
    qiwi_p2p.add(qiwi_p2p_but1)
    qiwi_p2p.add(qiwi_p2p_but2)
    qiwi_p2p.add(qiwi_p2p_but3)
    await state.finish()
    await callback_query.message.answer(f'''<strong>📒 Подготовленный счет к оплате</strong>\n\n💵 Сумма к оплате: <code>''' + str(parse) + '''</code> руб\n🥝 Номер киви: <code>''' + str(config.qiwi_number) + '''</code>\nКомментарий к платежу: <code>'''+str(randomber)+'''</code>\n\nВы можете скопировать сами просто нажав по реквизитам, либо использовать кнопки ниже\n\n🤖 После оплаты, нажмите кнопку "💷  Проверить оплату"\nПосле оплаты бот выдаст архив с интим-фото''',parse_mode='HTML', reply_markup=qiwi_p2p)

@dp.callback_query_handler(text='nick_oplata_full')
async def process_name(callback_query: types.CallbackQuery, state: FSMContext):
    img1 = open('temp/image_interface/oplata_pomoj_img.png', 'rb')
    await callback_query.message.answer_photo(photo=img1, reply_markup=prov_oplat_but)
    randomber = ''
    for x in range(12):
        randomber = randomber + random.choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'))
    global randomober
    parse = admin_panel.execute(f"SELECT full_price, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]
    price = parse
    link_oplata = f"https://qiwi.com/payment/form/99999?extra%5B%27account%27%5D="+config.nickname_qiwi+"&amountInteger="+price+"&amountFraction=0&extra%5B%27comment%27%5D="+randomber+"&currency=643&blocked%5B0%5D=sum&blocked%5B1%5D=comment&blocked%5B2%5D=account"
    qiwi_p2p: InlineKeyboardMarkup = types.InlineKeyboardMarkup()
    qiwi_p2p_but1 = types.InlineKeyboardButton("🥝 Перейти к оплате", url=link_oplata)
    qiwi_p2p_but3 = types.InlineKeyboardButton("🌀 Проверка оплаты", callback_data = f'check_payment_full_{randomber}')
    qiwi_p2p.add(qiwi_p2p_but1)
    qiwi_p2p.add(qiwi_p2p_but3)
    await state.finish()
    await callback_query.message.answer(f'''<strong>📒 Подготовленный счет к оплате</strong>\n\n💵 Сумма к оплате: <code>''' + str(parse) + '''</code> руб\n🥝 Ник киви: <code>''' + str(config.nickname_qiwi) + '''</code>\nКомментарий к платежу: <code>'''+str(randomber)+'''</code>\n\nВы можете скопировать сами просто нажав по реквизитам, либо использовать кнопки ниже\n\n🤖 После оплаты, нажмите кнопку "💷  Проверить оплату"\nПосле оплаты бот выдаст архив с интим-фото''',parse_mode='HTML', reply_markup=qiwi_p2p)

@dp.callback_query_handler(text='cart_oplata_full')
async def process_name(callback_query: types.CallbackQuery):
    img1 = open('temp/image_interface/oplata_pomoj_img.png', 'rb')
    randomber = ''
    for x in range(12):
        randomber = randomber + random.choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'))
    global bill
    parse = admin_panel.execute(f"SELECT full_price, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]
    price = parse
    lifetime = 5
    comment = randomber
    bill = p2p.bill(amount=price, lifetime=lifetime, comment=comment)
    link_oplata = bill.pay_url
    warnings.filterwarnings("ignore")
    qiwi_p2p = types.InlineKeyboardMarkup()
    qiwi_p2p_but = types.InlineKeyboardButton("💳 Оплатить с карты", url=link_oplata)
    qiwi_p2p_but2 = types.InlineKeyboardButton("💻 Проверить оплату", callback_data='prov_oplat_p2p_full')
    qiwi_p2p.add(qiwi_p2p_but)
    qiwi_p2p.add(qiwi_p2p_but2)
    id_tel_user = callback_query.from_user.id
    await callback_query.message.answer_photo(photo=img1, caption='💎 Подготовка формы для оплаты прошла успешно',reply_markup=prov_oplat_but)
    await callback_query.message.answer(f'''<strong>📒 Подготовленный счет к оплате</strong>\n\n💵 Сумма к оплате: <code>''' + str(parse) + '''</code> руб\n⏳ Счет действителен: <code>'''+str(lifetime)+'''</code> минуты\n\n🤖 После оплаты, нажмите кнопку "💷  Проверить оплату"\nПосле оплаты бот выдаст архив с интим-фото''', parse_mode='HTML', reply_markup=qiwi_p2p)

@dp.callback_query_handler(text = 'prov_oplat_p2p_full')
async def functionoplata(call: types.CallbackQuery):
    warnings.filterwarnings("ignore")
    id_tel_user = call.from_user.id
    status = p2p.check(bill_id=bill.bill_id).status
    if status == 'PAID':
        await call.message.edit_text(f'📒 Подготовленный счет к оплате\n\n✅ Счет был оплачен!\n\n👨‍💻 Благодарим за покупку подписки\n\n👁 Если возникли трудности с получением товара, то отпишите в тех.поддержку')
        doc = open('other/Imtimki' + '.rar', 'rb')
        await call.message.answer_document(doc)
        parse = admin_panel.execute(f"SELECT full_price, number_code FROM admin_panel_info where number_code=number_code").fetchone()[0]
        price = parse
        dolya = ((int(price) * int(config.prosent_work)) / 100)
        plata_worker = float(dolya)
        worker_ref = user_workers.execute(f"SELECT worker_referal, id_user FROM user_workers where id_user={id_tel_user}").fetchone()[0]
        user_workers.execute(f"UPDATE user_workers SET balanse_worker = balanse_worker + {plata_worker} WHERE id_user={worker_ref}")
        workers.commit()
        await bot.send_message(worker_ref,f"✅Успешная оплата мамонта\n💰Ваша доля: {dolya} рублей.\n🦣ID мамонта: {call.from_user.id}\n💳Деньги вывести сможете в боте тимы")
        await bot.send_message(channel_id_zalet,"🧞‍♂️ Воркер: " + str(worker_ref) + " занес нам бабки\n💰Cумма залета: " + str(price) + " рублей\n💰Доля воркера " + str(plata_worker) + "")
    else:
        await bot.send_message(call.from_user.id, '❎ Не было поступления платежа!')


###-------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

