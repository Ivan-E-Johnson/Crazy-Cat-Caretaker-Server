import time
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


@app.route("/login", methods=("GET", "POST"))
def login():
    if "user" in session:
        return redirect("/")
    if request.method == "POST":
        if "create_user" in request.form:
            return redirect("/signup")
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
        mac_address  = request.form.get("mac_address")
        success = Authentication.create_user(email, password, mac_address)
        if success:
            return redirect("/")
        return redirect(request.referrer)

    else:
        return render_template("signup.html")

@app.route("/logout")
def logout():
    # TODO ADD logout button
    session.pop("user")
    return redirect("/")


@app.route("/playing")
@Authentication.login_required
def playing():
    video_key = "TESTFEEDKEY"
    return render_template(
        "playing.html", video_key=video_key, started=video_key in Camera.feeds
    )


@app.route("/", methods=("GET", "POST"))
@Authentication.login_required
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
@Authentication.login_required
def stream():
    # TODO
    return "Success"


def gen(camera):
    while True:
        video_key = "TESTFEEDKEY"
        frame = camera.get_frame()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/video_feed")
@Authentication.login_required
def video_feed():
    print("here")
    return Response(gen(Camera()), mimetype="multipart/x-mixed-replace; boundary=frame")
