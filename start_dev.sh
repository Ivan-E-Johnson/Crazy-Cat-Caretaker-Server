export APPLICATION_SETTINGS=config.py

export FLASK_APP=app
export FLASK_DEBUG=true
gunicorn wsgi:app --worker-class gevent --bind 0.0.0.0:${1:-8000}
