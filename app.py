import time
<<<<<<< HEAD

import smtplib
from email.mime.text import MIMEText
=======
from typing import List
>>>>>>> 165a4ee (Teachable machine is working.)

from flask import (
    Flask,
    render_template,
    flash,
    request,
    redirect,
    abort,
    Response,
    session,
)
from flask_session import Session
from camera import Camera
import teachable_machine
import config
from flask_sse import sse
from redis import Redis
import pyrebase
import Authentication
from Home import Users, House, Cats, HomeEvents

#### VERY IMPORTANT
## FIXES BUG BETWEEN GUINICORN AND FIRESTORE
import grpc.experimental.gevent as grpc_gevent
grpc_gevent.init_gevent()
# https://stackoverflow.com/questions/57742213/gunicorn-worker-timeout-while-using-any-firestore-function-not-even-a-get
##### Removing will kill whole application

app = Flask(__name__)

# Configure Redis server for dynamic page updates
r = Redis()
app.config["REDIS_URL"] = "redis://localhost"
app.config.from_envvar("APPLICATION_SETTINGS")  # TODO send this to entire team so that we can access it
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.register_blueprint(sse, url_prefix="/stream")  # For sse events
Session(app)

status = {}
settings = {
    "classify_period": 1
}

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect("/")
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        Authentication.login(email, password)
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/signup", methods=("GET", "POST"))
def signup():
    if "user" in session:
        return redirect("/")
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        mac_address = request.form.get("mac_address")
        success = Authentication.create_user(email, password, mac_address)
        if success:
            return redirect("/")
        return redirect(request.referrer)

    else:
        return render_template("signup.html")


@app.route("/logout")
@Authentication.login_required
def logout():
    # TODO ADD logout button
    session.pop("user")
    return redirect("/")


@app.route("/feeding")
@Authentication.login_required
def feeding():
    return render_template("feeding.html")


@app.route("/playing", methods=["GET", "POST"])
@Authentication.login_required
def playing():
    video_key = "TESTFEEDKEY"
    return render_template(
        "playing.html", video_key=video_key, started=video_key in Camera.feeds
    )


@app.route("/view_profiles", methods=["GET", "POST"])
@Authentication.login_required
def view_profiles():
    return render_template("view_profiles.html")


@app.route("/add_cat", methods=["GET", "POST"])
@Authentication.login_required
def add_cat():
    return render_template("add_cat.html")


@app.route("/", methods=("GET", "POST"))
@Authentication.login_required
def landing_page():
    # if request.method == "GET":
        # if request.form["feeding_button"] == "clicked":
        #     flash("TODO: Feeding the cat page")
        #     return render_template("feeding.html")
        # if request.form["logout_button"] == "clicked":
        #     flash("Logged out")
        #     return render_template("login.html")
    #     if request.form["playing_button"] == "clicked":
    #         flash("TODO: Laser pointer control page")
    #         return render_template("playing.html")
    return render_template("landing_page.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    mac_address = "123445677" # TODO CHANGE ME
    file = request.files["media"]
    # filename = file.filename
    image = file.read()
    Camera.feeds[mac_address] = image
    sse.publish({"started": True}, type=mac_address)

    last_classified = status.get(mac_address, {}).get("last_classified", None)
    if last_classified is None or last_classified + settings["classify_period"] < time.time():
        if mac_address not in status:
            status[mac_address] = {}
        status[mac_address]["last_classified"] = 0
        cat_class, probability = teachable_machine.classify(image)
        status[mac_address]["last_classified"] = time.time()
        if cat_class != teachable_machine.NO_CAT:
            cat_house: House = House.get(mac_address)
            cats: List[Cats] = cat_house.cats
            cat = None
            for house_cat in cats:
                if house_cat.name == cat_class:
                    print("CAT FOUND", house_cat.name)
                    cat = house_cat
                    cat.name = "TESTSTETST"
                    print(cat)
            assert cat is not None # Should handle this better but we are making some assumptions for now
            print(cat_house)

    # We cannot save files directly after reading them or vice versa
    # file.save(filename)
    return "Success"


@app.route("/stream", methods=["POST"])
@Authentication.login_required
def stream():
    # TODO
    return "Success"


def gen(camera: Camera):
    while True:
        frame = camera.get_frame()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/video_feed")
@Authentication.login_required
def video_feed():
    print("here")
    video_key = session["mac_address"]
    return Response(gen(Camera(video_key)), mimetype="multipart/x-mixed-replace; boundary=frame")


def email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, recipients, msg.as_string())
    smtp_server.quit()


@app.route("/send_email", methods=["GET", "POST"])
def send_email():
    subject = "Test"
    body = "This is a test"
    sender = "crazycatcaretaker123@gmail.com"
    recipients = ["crazycatcaretaker123@gmail.com"]
    password = "wklhkcqzccnkgsvr"

    print("hello!")
    return email(subject, body, sender, recipients, password)
