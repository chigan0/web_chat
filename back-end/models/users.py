from typing import Union, List, Dict, Optional, Tuple
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, and_, or_, desc, func
from sqlalchemy.orm import relationship, Session

from extensions import db, login_manager


class Personal(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	login = db.Column(db.String(32), nullable=False, unique=True)
	password = db.Column(db.String(512), nullable=False)
	is_admin = db.Column(db.Boolean, default=False)
	date_create = Column(DateTime(timezone=True), onupdate=func.now())

	def get_json(self,):
		return {'login': self.login, 'is_admin': self.is_admin}


class Users(db.Model):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True)
	tg_id = Column(String(25), unique=True)
	first_name = Column(String(75), nullable=False)
	username = Column(String(45), nullable=True)
	fake_name = Column(String(45), nullable=False)
	fake_surname = Column(String(45), nullable=False)
	bio = Column(String(75), nullable=True)
	note = Column(String(60), nullable=True, default='Примечание')
	date_create = Column(DateTime)
	last_message_r = db.relationship('LastMessage', backref='last_user_message', lazy='joined', uselist=False)

	def __repr__(self,):
		return f"TH ID - {self.tg_id}"

	def get_json(self):
		data = self.__dict__.copy()
		del data['_sa_instance_state']
		del data['last_message_r']
		return data


@login_manager.user_loader
def load_user(user_id):
	return Personal.query.get(user_id)


def add_new_personal(login, password, is_admin):
	return Personal(login=login, password=password, is_admin=is_admin, date_create=datetime.now())


def get_user_by_login(login):
	return Personal.query.filter_by(login=login).first()


def get_all_users(is_staff=False):
	if is_staff:
		return Users.query.all()

	return Users.query.with_entities(Users.id, Users.fake_name, Users.fake_surname, Users.note).all()

def get_user_by_tg_login(login):
	return Users.query.filter(Users.username.like(f"{login}%")).limit(15).all()


def get_user_by_fake_name(name):
	return Users.query.filter(or_(Users.fake_name.like(f"{name}%"), Users.fake_surname.like(f"{name}%"))).limit(15).all()


def get_client_by_id(user_id):
	return Users.query.filter(Users.id == user_id).one_or_none()
