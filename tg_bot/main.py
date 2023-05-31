import asyncio
from os import system
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.types import FSInputFile

import models
from models.users import get_user_by_id
from models.chat import get_last_message_by_id
from settings import settings
from handlers import command
from redis_conn import redis_pool
from util.utils import get_fake_username, pickle_data_dumps
from db import Base, engine, get_db, db_connect


async def message_from_support(bot: Bot):
	redis_session = await redis_pool()
	pubsub = redis_session.pubsub()

	await pubsub.subscribe("new_support_from_message")

	while True:
		message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
		if message is not None:
			data = pickle_data_dumps(message['data'], True)

			# with get_db(True) as session:
			session = db_connect()
			user = await get_user_by_id(session, data['user_id'])

			if user is not None:
				last_message_r = await get_last_message_by_id(session, user.id)
				last_message_r.last_message_data = datetime.now()

				if (data['message_obj']['file_state']):
					while True:
						try:
							photo = FSInputFile(f"{settings.STATIC_DIR}/{data['message_obj']['file_name']}")
							await bot.send_photo(user.tg_id, photo=photo, caption=data['message_obj']['message'])
							break
						except: continue

				else:
					while True:
						try: 
							await bot.send_message(user.tg_id, data['message'])
							break
						except: continue

			session.commit()


		await asyncio.sleep(0.1)


async def main():
	bot = Bot(token=settings.TOKEN, parse_mode='html')
	dp = Dispatcher()
	dp.include_router(command.router)
	
	Base.metadata.create_all(bind=engine)
	asyncio.create_task(message_from_support(bot))

	print("BOT WORKS")
	await bot.delete_webhook(drop_pending_updates=True)
	await dp.start_polling(bot, none_stop=True)


if __name__ == '__main__':
	while True:
		try:
			# system('cls')
			asyncio.run(main())
	
		except KeyboardInterrupt:
			print("\n@GoodBye :)")
			break

		except Exception:
			continue
