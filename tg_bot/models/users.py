from typing import Union, List, Dict, Optional, Tuple
from datetime import datetime

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, and_, or_, func
from sqlalchemy.orm import relationship, Session

from db import Base

class Users(Base):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True)
	tg_id = Column(String(25), unique=True)
	first_name = Column(String(75), nullable=False)
	username = Column(String(45), nullable=True)
	fake_name = Column(String(45), nullable=False)
	fake_surname = Column(String(45), nullable=False)
	bio = Column(String(75), nullable=True)
	note = Column(String(60), nullable=True, default='Примечание')
	date_create = Column(DateTime(timezone=True))
	last_message_r = relationship('LastMessage', backref='last_user_message', lazy='joined', uselist=False)

	def __repr__(self,):
		return f"TH ID - {self.tg_id}"

	def get_json(self,):
		data = self.__dict__.copy()
		del data['_sa_instance_state']

		return data


def create_user(session: Session, user_data: object, fake_username: str, fake_surname: str) -> None:
	user = Users(tg_id=user_data.id, first_name=user_data.first_name, username=user_data.username,
				 fake_name=fake_username, fake_surname=fake_surname, bio=user_data.bio, date_create=datetime.now())

	session.add(user)
	session.commit()
	session.refresh(user)

	return user


async def check_user(session: Session, user_tg_id: int) -> Union[Users, None]:
	return session.query(Users).filter(Users.tg_id == user_tg_id).one_or_none()


async def get_user_by_id(session: Session, user_id: int) -> Union[Users, None]:
	return session.query(Users.id, Users.tg_id).filter(Users.id == user_id).one_or_none()
