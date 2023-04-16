import time

from flask import Flask, render_template, flash, request, redirect, abort, Response
from camera import Camera
import teachable_machine
from flask_sse import sse
from redis import Redis

app = Flask(__name__)

# Configure Redis server for dynamic page updates
r = Redis()
app.config["REDIS_URL"] = "redis://localhost"
app.config.from_envvar("APPLICATION_SETTINGS")

app.register_blueprint(sse, url_prefix="/stream")  # For sse events


@app.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        flash(
            f"TODO Implement login authentication. Username {request.form['username']}"
        )
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/playing")
def playing():
    video_key = "TESTFEEDKEY"
    return render_template("playing.html", video_key=video_key, started=video_key in Camera.feeds)


@app.route("/", methods=("GET", "POST"))
def landing_page():
    if request.method == "POST":
        if request.form["button"] == "Button1":
            flash("TODO: Feeding the cat page")
            return render_template("feeding.html", title="Land")
        else:
            flash("TODO: Laser pointer control page")
            return redirect("/playing")
    return render_template("landing_page.html", title="Land")


@app.route("/upload", methods=["POST"])
def upload_file():
    video_key = "TESTFEEDKEY"
    file = request.files["media"]
    # filename = file.filename
    image = file.read()
    Camera.feeds[video_key] = image
    sse.publish({"started": True}, type=video_key)
    # sse.publish({"message": "Hello!!"}, type='greeting')
    # print("message sent. done")
    # print(teachable_machine.classify(image))

    # We cannot save files directly after reading them or vice versa
    # file.save(filename)
    return "Success"


@app.route("/stream", methods=["POST"])
def stream():
    # TODO
    return "Success"


def gen(camera):
    while True:
        video_key = "TESTFEEDKEY"
        frame = camera.get_frame()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/video_feed")
def video_feed():
    print("here")
    return Response(gen(Camera()), mimetype="multipart/x-mixed-replace; boundary=frame")
