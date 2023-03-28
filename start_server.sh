export APPLICATION_SETTINGS=config.py

export FLASK_APP=app
export FLASK_DEBUG=true
# TODO SETUP REDIS SERVER
docker pull redis

gunicorn wsgi:app --worker-class gevent --bind :8000

