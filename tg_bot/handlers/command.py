import asyncio
from typing import List
from datetime import datetime

import aiohttp
from aiogram import Router, Bot, types, F
from aiogram.types import Message, CallbackQuery, FSInputFile, ContentType as CT
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.exceptions import TelegramForbiddenError

from settings import settings
from db import get_db, db_connect
from models.users import check_user, create_user
from models.chat import create_last_message, add_new_message
from util.utils import get_fake_username, pickle_data_dumps, random_str
from redis_conn import redis_pool

router = Router()

async def new_user(user_data):
	# with get_db(True) as session:
	session = db_connect()
	fake_username, fake_surname = get_fake_username()
	user = create_user(session, user_data, fake_username, fake_surname)
	last_message = create_last_message(session, user.id)
	session.commit()
	session.refresh(last_message)


async def check_user_info(tg_id, user_data, bot, message):
	bio = user_data.bio
	first_name = user_data.first_name
	username = user_data.username

	session = db_connect()
	user = await check_user(session, tg_id)

	if (user is None):
		await new_user(user_data)
		await send_message_to_support(message, bot)

	elif first_name != user.first_name or username != user.username or bio != user.bio:
		fake_username, fake_surname = get_fake_username()
		redis_session = await redis_pool()

		user.bio = bio
		user.first_name = first_name
		user.username = username 
		user.fake_name = fake_username
		user.fake_surname = fake_surname
		session.commit()

		await redis_session.publish("update_user_info", pickle_data_dumps({'user_id': user.id, 'fake_name': user.fake_name, 
																		   'fake_surname': user.fake_surname, 'note': user.note}))


@router.message(Command(commands=['start']))
async def cmd_send_welcome(message: Message, bot: Bot, state: FSMContext):
	user_tg_id = message.from_user.id

	# with get_db() as session:
	session = db_connect()
	user_state = await check_user(session, user_tg_id)
		
	if user_state is None:
		user_data = await bot.get_chat(message.from_user.id)
		asyncio.create_task(new_user(user_data))
	
	await message.delete()
	await message.answer('Вас приветствует бот тех. Поддержки \nНапишите интересующий вас вопрос')


@router.message(F.content_type.in_([CT.TEXT, CT.PHOTO]))
async def send_message_to_support(message: Message, bot: Bot):
	user_data = await bot.get_chat(message.from_user.id)
	asyncio.create_task(check_user_info(message.from_user.id, user_data, bot, message))

	redis_session = await redis_pool()
	user_message = message.text
	file_name = None
	file_state = False
	file_type = None

	if (message.photo is not None):
		file_type = 'image'
		file_state = True
		file_name = f"{random_str(10)}.jpg"
		file_info = await bot.get_file(message.photo[-1].file_id)
		new_photo = await bot.download_file(file_info.file_path, f"{settings.STATIC_DIR}/{file_name}")
		user_message = 'Фото без текста' if message.caption is None else message.caption

	if (message.forward_from is not None):
		user_message = f"<b>Пересланное сообщение от - {message.forward_from.first_name}</b> <hr> {user_message}"
	
	elif (message.forward_from_chat is not None):
		user_message = f"<b>Пересланное сообщение из канала - {message.forward_from_chat.title}</b> <hr> {user_message}"

	elif (message.forward_sender_name is not None):
		user_message = f"<b>Пересланное сообщение от - {message.forward_sender_name}</b> <hr> {user_message}"

	session = db_connect()
	user = await check_user(session, message.from_user.id)

	if user is not None:
		await redis_session.set(user.id, 'sender')
		obj_message = add_new_message(session, user.id, 'sender', user_message, file_state, file_type, file_name)
		user.last_message_r.last_message_data = datetime.now()
		await redis_session.publish("new_message_from_tg", pickle_data_dumps({"fake_name": user.fake_name, "fake_surname": user.fake_surname, 
																			  "user_id": user.id, 'note': user.note,
																			  "message_id": obj_message.id, "message_data": obj_message.get_json()}))
		session.commit()
