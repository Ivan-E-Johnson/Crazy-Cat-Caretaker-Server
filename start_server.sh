export APPLICATION_SETTINGS=config.py

export FLASK_APP=app
export FLASK_DEBUG=true
# TODO SETUP REDIS SERVER
pip install gunicorn

# this takes a while. A different way would be better
# TODO MUST DO HERE DOWN MANUALLY
sudo su -c "apt-get update && apt-get install ffmpeg libsm6 libxext6  -y"

docker pull redis
docker run --rm --name local-redis -p 6379:6379 -d redis

# docker run --rm --name local-redis -p 6379:6379 -d redis-server
gunicorn wsgi:app --worker-class gevent --bind :8000


# MUST CHANGE port 8000 AND port 6379 to PUBLIC
