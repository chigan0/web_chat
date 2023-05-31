from resources import views
from resources.chat import (
	create_ws, 
	get_user_list, 
	find_user, 
	chat_history, 
	get_user_info, 
	messages_with_file)

def setup_routes(app, socketio):
	# Templates 
	app.add_url_rule('/chat', view_func=views.chat_template, methods=['GET'])
	app.add_url_rule('/login', view_func=views.login_template, methods=['GET', 'POST'])
	app.add_url_rule('/logout', view_func=views.logout, methods=['GET'])
	app.add_url_rule('/ticket', view_func=views.get_ticket, methods=['GET'])
	app.add_url_rule('/get_user_list', view_func=get_user_list, methods=['GET'])
	app.add_url_rule('/search_user', view_func=find_user, methods=['GET'])
	app.add_url_rule('/chat_history', view_func=chat_history, methods=['GET'])
	app.add_url_rule('/user_info', view_func=get_user_info, methods=['GET'])
	app.add_url_rule('/staff/registration', view_func=views.staff_registration, methods=['GET', 'POST'])
	app.add_url_rule('/support/message', view_func=messages_with_file, methods=['GET', 'POST'])
	# app.add_url_rule('/registration', view_func=views.registration, methods=['GET', 'POST'])

	# Soscket
	create_ws(socketio)
	#socketio.on_event('my event', views.my_function_handler, namespace='/test')
