import redis
from datetime import timedelta
from random import choice
from flask import render_template, request, redirect, url_for, current_app
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from settings import settings
from .chat import pickle_data_dumps
from models.users import get_user_by_login, add_new_personal


def login_template():
	if request.method == 'GET':
		return render_template('login.html')

	error_message = ""
	login = request.form.get('login')
	password = '' if request.form.get('password') is None else request.form.get('password')

	user = get_user_by_login(login)

	if user is not None and check_password_hash(user.password, password):
		login_user(user)
		return redirect(url_for('chat_template'), code=302)
	
	if user is None: 
		error_message="Неверный логин"
	
	elif not check_password_hash(user.password, password): 
		error_message="Неверный пароль"
	
	return render_template('login.html', error_state=True, error_message=error_message)


@login_required
def get_ticket():
	ticket = ''.join([choice(list('abcdefghijklmnopqrstuvwxyz1234567890')) for _ in range(10)])
	redis_session = redis.from_url(settings.REDIS_DSN)

	redis_session.set(ticket, pickle_data_dumps(current_user.get_json()), timedelta(days=6))
	return {"ticket": ticket, "profile_info": current_user.get_json()}


@login_required
def logout():
	logout_user()
	return redirect(url_for('login_template'), code=302)


@login_required
def registration():
	if request.method == 'GET':
		return render_template('registration.html')


@login_required
def chat_template():
	return render_template('chat.html', staff=current_user.is_admin)


@login_required
def staff_registration():
	staff = current_user.is_admin 

	if not staff:
		return redirect(url_for('chat_template'), code=302)

	if request.method == 'GET':
		if staff:
			return render_template('staff_registration.html')

	login = request.form.get('login')
	password = request.form.get('password')
	pssword_confirm = request.form.get('password_confirm')
	admin_state = True if request.form.get('admin_state') == 'on' else False

	if len(login) < 1 or len(password) < 2 or len(pssword_confirm) < 2:
		return render_template('staff_registration.html', error_state=True, error_message='Не все поля заполненный')

	if password != pssword_confirm:
		return render_template('staff_registration.html', error_state=True, error_message='Пароли не совпадают')

	if get_user_by_login(login) is not None:
		return render_template('staff_registration.html', error_state=True, error_message='Пользователь с таким логином уже существует')

	personal = add_new_personal(login, generate_password_hash(password), admin_state)
	db.session.add(personal)
	db.session.commit()

	return redirect(url_for('chat_template'), code=302)
