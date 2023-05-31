from typing import Union, List, Dict, Optional, Tuple
from datetime import datetime

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, and_, or_, func
from sqlalchemy.orm import relationship, Session

from db import Base

class LastMessage(Base):
	__tablename__ = 'last_message'

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('users.id'))
	last_message_data = Column(DateTime)

	def __repr__(self,):
		return str(self.last_message_data)


class Messages(Base):
	__tablename__ = 'messages'

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, nullable=False)
	message_class = Column(String(25), nullable=False)
	message = Column(String(5000), nullable=False)
	file_state = Column(Boolean, default=False)
	file_type = Column(String(25), nullable=True)
	file_name = Column(String(80), nullable=True)
	date_create = Column(DateTime)

	def __repr__(self,):
		return f"{str(self.user_id)} message_class - {self.message_class}"

	def get_json(self,):
		data = self.__dict__.copy()
		del data['_sa_instance_state']

		data['date_create'] = data['date_create'].strftime("%H:%M")
		return data


def create_last_message(session: Session, user_id: int) -> LastMessage:
	last_mes = LastMessage(user_id=user_id, last_message_data=datetime.now())
	session.add(last_mes)
	return last_mes


def add_new_message(session: Session, user_id, message_class, message, file_state = False, file_type = None, file_name = None):
	obj_message = Messages(user_id=user_id, message_class=message_class, message=message, 
					   file_state=file_state, file_type=file_type, file_name=file_name, date_create=datetime.now())

	session.add(obj_message)
	session.commit()
	session.refresh(obj_message)
	return obj_message


async def get_last_message_by_id(session: Session, user_id: int):
	return session.query(LastMessage).filter(LastMessage.user_id == user_id).one_or_none()
