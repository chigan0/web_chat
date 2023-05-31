import threading
import asyncio

from flask import Flask, render_template
from flask_cors import CORS
from flask_socketio import SocketIO
from werkzeug.security import check_password_hash, generate_password_hash

import models
from models.users import get_user_by_login
from router import setup_routes
from settings import Settings
from extensions import db, login_manager
from resources.chat import interception_tg_message


def tg_message(socketio):
	asyncio.run(interception_tg_message(socketio))


def create_app():
	app = Flask(__name__, static_folder="static")
	app.config.from_object(Settings)
	cors = CORS(app)
	socketio = SocketIO(app)

	CORS(app, resources={f"/*": {"origins": "*"}})
	db.init_app(app)
	
	with app.app_context():
		db.create_all()

		if get_user_by_login('root_gb') is None:
			db.session.add(models.Personal(login='root_gb', password=generate_password_hash('Admin_-132442'), is_admin=True))
			db.session.commit()

	login_manager.init_app(app)
	setup_routes(app, socketio)

	threading.Thread(target=tg_message, daemon=True, args=(socketio,)).start()

	@app.errorhandler(401)
	def not_found(e):
		return render_template('custom_401-page.html'), 401

	@app.errorhandler(404)
	def not_found(e):
		return render_template('custom_404-page.html'), 404

	return app, socketio
