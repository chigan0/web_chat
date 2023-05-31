import os
import asyncio
from random import choice
from typing import Union
from pickle import loads, dumps

import aioredis
import redis
from flask import request
from flask_login import login_required, current_user
from flask_socketio import SocketIO, emit, ConnectionRefusedError

from extensions import db
from settings import settings
from models.users import get_all_users, get_user_by_fake_name, get_client_by_id, get_user_by_tg_login
from models.chat import get_last_message_list, add_new_message, get_user_message


socketioG = None


def random_str(length:int=16) -> str:
	symb = 'abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	return ''.join((choice(symb) for i in range(length)))


def pickle_data_dumps(data: Union[dict, object], status: bool = False) -> Union[bytes, dict]:
	if data is None:
		return None

	if status:
		return loads(data)

	else:
		if type(data) == dict:
			picke_dumps = {}
			for i in data:
				picke_dumps[i] = data[i]
		else:
			picke_dumps = data

		return dumps(picke_dumps)


async def interception_tg_message(socketio):
	redis_session = aioredis.from_url("redis://localhost", decode_responses=False, socket_timeout=0.5, health_check_interval=20)

	pubsub = redis_session.pubsub()
	await pubsub.subscribe("new_message_from_tg")
	await pubsub.subscribe("update_user_info")

	try:
		while True:
			message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
			if message is not None:
				data = pickle_data_dumps(message['data'], True)
				socketio.emit(message['channel'].decode('utf-8'), data)

			await asyncio.sleep(0.1)

	except Exception as e:
		print("ERROR", e)


def create_ws(socketio):
	global socketioG
	socketioG = socketio

	@socketio.on('connect')
	def socket_connect():
		ticket = request.args.get('ticket')

		if request.args.get('ticket') is None:
			return socketio.emit('redirect')

		redis_session = redis.from_url(settings.REDIS_DSN)
		redis_session.get(ticket)

		if request.args.get('ticket') is None:
			return socketio.emit('redirect')

		redis_session.close()


	@socketio.on('change_note')
	def change_user_noti(data):
		message: str = data.get('message')
		user_id: int = data.get('user_id')

		if (message is None or user_id is None):
			return

		user = get_client_by_id(user_id)

		if user is None:
			return

		user.note = message
		db.session.add(user)
		db.session.commit()
		socketio.emit('update_user_note', {'user_id': user_id, 'note': message})


	@socketio.on('new_message_from_support')
	def new_message_from_support(data):
		message = data.get('message')
		user_id = data.get('user_id')
		ticket = data.get('ticket')

		if ticket is None:
			return socketio.emit('redirect')

		redis_session = redis.from_url(settings.REDIS_DSN)
		user_data = pickle_data_dumps(redis_session.get(ticket), True)
		
		if user_data is None:
			socketio.emit('redirect')

		last_message = redis_session.get(user_id)
		if last_message is not None and last_message.decode() == 'repaly' and user_data['is_admin'] == False:
			return

		if message is not None and user_id is not None:
			obj_message = add_new_message(user_id, 'repaly', message)
			db.session.add(obj_message)
			db.session.commit()
			db.session.refresh(obj_message)
			redis_session.set(user_id, 'repaly')

			redis_session = redis.from_url(settings.REDIS_DSN)
			redis_session.publish("new_support_from_message", pickle_data_dumps({"user_id": user_id, "message": message, 
																				 "message_obj": obj_message.get_json()}))
			socketio.emit('update_support_message', {'user_id': user_id, 'message_id': obj_message.id, 'message_data': obj_message.get_json()})


@login_required
def get_user_list():
	staff = current_user.is_admin
	users = get_all_users(staff)
	user_id_list = []
	data = {}

	for user, last_message in zip(users, get_last_message_list()):
		user_id_list.append(last_message.user_id)
		data[user.id] = {'fake_name': user.fake_name, 'fake_surname': user.fake_surname, 'note': user.note}

		if staff:
			data[user.id] = {**data[user.id], **user.get_json()}


	# await asyncio.sleep(0.3)
	return {'users_id_list': user_id_list, "user_data": data}


@login_required
def find_user():
	data = []
	name = request.args.get("name")
	if name is None or len(name) < 1:
		return {}

	if current_user.is_admin: data = get_user_by_tg_login(name)
	else: data = get_user_by_fake_name(name)

	return {user.id: {'fake_name': user.fake_name, 'fake_surname': user.fake_surname, 'note': user.note} for user in data}


@login_required
def chat_history():
	if (len(request.args) == 0):
		return {}

	result = {int(user_id): {} for user_id in request.args.getlist("user_id")}
	data = get_user_message(request.args.getlist("user_id"), current_user.is_admin)

	for mes in data:
		result[mes.user_id][mes.id] = mes.get_json()

	return result


@login_required
def get_user_info():
	staff = current_user.is_admin
	user_id = request.args.get('user_id')

	if not staff or user_id is None:
		return {}

	user = get_client_by_id(user_id)
	return user.get_json() if user is not None else {}


@login_required
def messages_with_file():
	user_id = request.form.get('user_id')
	message = 'Файл от тех. Поддержки' if len(request.form.get('message')) == 0 else request.form.get('message')
	file = request.files.get('image')

	if user_id is None or file is None:
		return {}

	if not (file.filename.split('.')[-1].lower() in ['png', 'jpg', 'jpeg']):
		return {}

	filename = f"{random_str(10)}.jpg"
	file.save(os.path.join(settings.UPLOAD_FOLDER, filename))

	obj_message = add_new_message(user_id, 'repaly', message, True, 'image', filename)
	db.session.add(obj_message)
	db.session.commit()
	db.session.refresh(obj_message)

	redis_session = redis.from_url(settings.REDIS_DSN)
	redis_session.publish("new_support_from_message", pickle_data_dumps({"user_id": user_id, "message": message, "message_obj": obj_message.get_json()}))
	socketioG.emit('update_support_message', {'user_id': int(user_id), 'message_id': obj_message.id, 'message_data': obj_message.get_json()})

	return {}
