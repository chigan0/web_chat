# import eventlet
# from eventlet import wsgi

from app import create_app

app, socketio = create_app()
# eventlet.monkey_patch()

if __name__ == "__main__":
	socketio.run(app)
	# wsgi.server(eventlet.listen(("127.0.0.1", 5000)), app)
