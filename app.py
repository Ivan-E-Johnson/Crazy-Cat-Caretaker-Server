import time
from flask import Flask, render_template, flash, request, redirect, abort, Response, session
from flask_session import Session
from camera import Camera
import teachable_machine
import config
from flask_sse import sse
from redis import Redis
import pyrebase
import Authentication

app = Flask(__name__)

# Configure Redis server for dynamic page updates
r = Redis()
app.config["REDIS_URL"] = "redis://localhost"
app.config.from_envvar("APPLICATION_SETTINGS") #TODO send this to entire team so that we can access it
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.register_blueprint(sse, url_prefix="/stream")  # For sse events
Session(app)
################################################################
# AUTHENTICATION


firebase = pyrebase.initialize_app(Authentication.AUTH_CONFIG)
auth = firebase.auth()
################################################################
@app.route("/login", methods=("GET", "POST"))
def login():
    if 'user' in session:
        return redirect("/")
    if request.method == "POST":
        flash(
            f"TODO Implement login authentication. Email {request.form['email']}"
        )
        email = request.form.get("email")
        password = request.form.get("password")
        print(f'Email: {email} \t Password: {password}')
        try:
            #
            #TODO fix this to work and not just create user
            if "create_user" in request.form:
                user = auth.create_user_with_email_and_password(email, password)
                flash(f"Created New User: {email}!")
            else:
                user = auth.sign_in_with_email_and_password(email, password)
                flash(f"Signed in as {email}!")
            print(user)
            session['user'] = user
        except Exception as e:
            print(repr(e))
            flash(f"Failed to log with error message: {e}")
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/playing")
def playing():
    video_key = "TESTFEEDKEY"
    return render_template("playing.html", video_key=video_key, started=video_key in Camera.feeds)

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect("/")

#TODO ADD logout button

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
