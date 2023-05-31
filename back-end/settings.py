import os

from pydantic import RedisDsn


class Settings:
	DEBUG = True
	BASE_DIR = os.path.dirname(os.path.realpath(__file__))
	SECRET_KEY: str = '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
	REDIS_DSN: RedisDsn = 'redis://localhost'
	SQLALCHEMY_DATABASE_URI: str = "mysql+pymysql://mysql_root:Sql_-132442@localhost/support"
	ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg',}
	SQLALCHEMY_POOL_SIZE: int = 10
	JSON_AS_ASCII: bool = False
	UPLOAD_FOLDER: str = f"{BASE_DIR}/static/images"


settings = Settings()
