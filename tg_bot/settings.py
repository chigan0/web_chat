import os
import sys
from pathlib import Path

from pydantic import BaseSettings, RedisDsn


class Settings(BaseSettings):
	BASE_DIR: str = os.path.dirname(os.path.realpath(__file__))
	STATIC_DIR: str = os.path.join(os.path.dirname(os.path.realpath('.')), "back-end/static/images")
	TOKEN: str = "6124796864:AAFgGyp7MR-pBeDq_lGSgVSWbFGCd2OqpqA"
	REDIS_DSN: RedisDsn = 'redis://localhost'
	SQLALCHEMY_DATABASE_URL: str = "mysql+pymysql://mysql_root:Sql_-132442@localhost/support"


settings = Settings()
