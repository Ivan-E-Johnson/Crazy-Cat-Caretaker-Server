from threading import Thread

from flask import Flask, render_template, flash, request, redirect, abort
import teachable_machine
from flask_sse import sse
from redis import Redis
from rq import Queue

app = Flask(__name__)
r = Redis()
app.config.from_envvar("APPLICATION_SETTINGS")

# TODO redis needed for SSE, what does it do?
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')  # For sse events


@app.route("/")
def hello_world():
    return render_template("index.html", title="This is a test", utc_dt="hi")



@app.route("/login", methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        flash(request.form['username'])
        return redirect("/landing")
    else:
        return render_template("login.html")


@app.route("/index", methods=('GET', 'POST'))
def example():
    if request.method == "POST":
        flash("Feeding the Cat")
    return render_template("index.html", title="Index")


@app.route("/landing", methods=('GET', 'POST'))
def landing_page():
    if request.method == "POST":
        if request.form['button'] == 'Button1':
            return 'Feeding cat '
        else:
            return 'Playing with cat'
    return render_template("landing_page.html", title="Land")

@app.route("/touch")
def touch():
    return render_template("touch.html", title="Hello")


@app.route("/video")
def video():
    return render_template("video.html", title="Hello")

@app.route('/upload', methods=['POST'])
def upload_file():
    print(request.files["media"])
    file = request.files["media"]
    filename = file.filename
    image = file.read()

    sse.publish({"message": "Hello!"}, type='greeting')
    print(teachable_machine.classify(image))

    # We cannot save files directly after reading them or vice versa
    # file.save(filename)
    return "Success"
