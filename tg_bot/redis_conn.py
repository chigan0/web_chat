import asyncio
from typing import Union, Optional, Dict
from datetime import datetime, timedelta

from aioredis import from_url

from settings import settings


async def redis_pool(decode_responses: bool = False) -> from_url:
	redis = await from_url(settings.REDIS_DSN, decode_responses=decode_responses)

	return redis
