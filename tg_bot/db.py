from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import settings


engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, pool_size=20, max_overflow=5)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def db_connect() -> sessionmaker:
	db = SessionLocal()
	return db


@contextmanager
def get_db(autocommit = False):
	connect = db_connect()
	try:
		yield connect
		if autocommit:
			connect.commit()
	except Exception as e:
		connect.rollback()
		raise e	

	finally:
		connect.close()

