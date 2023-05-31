from typing import Union, List, Dict, Optional, Tuple
from datetime import datetime, timedelta

from flask_login import UserMixin
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, and_, or_, desc, func
from sqlalchemy.orm import relationship, Session

from extensions import db, login_manager


class LastMessage(db.Model):
	__tablename__ = 'last_message'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	last_message_data = Column(DateTime)

	def __repr__(self,):
		return str(self.last_message_data)


class Messages(db.Model):
	__tablename__ = 'messages'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, nullable=False)
	message_class = db.Column(db.String(25), nullable=False)
	message = db.Column(db.String(5000), nullable=False)
	file_state = db.Column(db.Boolean, default=False)
	file_type = db.Column(db.String(25), nullable=True)
	file_name = db.Column(db.String(80), nullable=True)
	date_create = db.Column(DateTime)

	def __repr__(self,):
		return f"{str(self.user_id)} message_class - {self.message_class}"

	def get_json(self,):
		data = self.__dict__.copy()
		del data['_sa_instance_state']

		data['date_create'] = data['date_create'].strftime("%H:%M")

		return data


def get_last_message_list():
	return LastMessage.query.order_by(desc(LastMessage.last_message_data)).all()


def add_new_message(user_id, message_class, message, file_state = False, file_type = None, file_name = None):
	return Messages(user_id=user_id, message_class=message_class, message=message, 
					   file_state=file_state, file_type=file_type, file_name=file_name, date_create=datetime.now())


def get_user_message(user_id_list, staff_state: bool = False):
	last_message_time = datetime.now() - timedelta(days=30)

	return Messages.query.filter(Messages.user_id.in_(user_id_list), 
								 True if staff_state else Messages.date_create > last_message_time
								 ).order_by(desc(Messages.date_create)).all()
