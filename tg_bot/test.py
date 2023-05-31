import asyncio

import aioredis

from util.utils import pickle_data_dumps

async def main():
	redis = aioredis.from_url("redis://localhost", decode_responses=False, socket_timeout=0.5, health_check_interval=20)

	pubsub = redis.pubsub()
	await pubsub.subscribe("new_message")

	while True:
		message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
		if message is not None:
			print(pickle_data_dumps(message['data'], True))

		await asyncio.sleep(0.1)


asyncio.run(main())