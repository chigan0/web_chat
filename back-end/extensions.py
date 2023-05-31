import flask_login
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
login_manager = flask_login.LoginManager()
# login_manager.login_view = 'login_template'
