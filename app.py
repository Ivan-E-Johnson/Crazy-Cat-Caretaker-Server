import time
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

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
from Home import Users, House, Cats, HomeEvents, Notifications
import time
from datetime import datetime

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


@app.route("/laser_up_down")
@Authentication.login_required
def laser_up_down():
    house: House = House.get(session["mac_address"])
    house.events.laser_state = "up_down"
    house.events.laser_changed = True
    house.create()
    flash("Laser state updated")
    return redirect('/playing')


@app.route("/laser_side_side")
@Authentication.login_required
def laser_side_side():
    house: House = House.get(session["mac_address"])
    house.events.laser_state = "side_side"
    house.events.laser_changed = True
    house.create()
    flash("Laser state updated")
    return redirect('/playing')


@app.route("/laser_circle")
@Authentication.login_required
def laser_circle():
    house: House = House.get(session["mac_address"])
    house.events.laser_state = "circle"
    house.events.laser_changed = True
    house.create()
    flash(f"Laser state updated")
    return redirect('/playing')


@app.route("/laser_random")
@Authentication.login_required
def laser_random():
    house: House = House.get(session["mac_address"])
    house.events.laser_state = "random"
    house.events.laser_changed = True
    house.create()
    flash(f"Laser state updated")
    return redirect('/playing')


@app.route("/laser_off")
@Authentication.login_required
def laser_off():
    house: House = House.get(session["mac_address"])
    house.events.laser_state = "off"
    house.events.laser_changed = True
    house.create()
    flash(f"Laser state updated")
    return redirect('/playing')


@app.route("/feeding", methods=["GET", "POST"])
@Authentication.login_required
def feeding():
    if request.method == 'POST':
        cat_name = request.form.get("pick_cat")
        food_amount = request.form.get("pick_amount")
        house = House.get(session["mac_address"])

        cats: List[Cats] = house.cats
        cat = None
        for house_cat in cats:
            if house_cat.name == cat_name:
                print("CAT FOUND", house_cat.name)
                cat = house_cat
        assert cat is not None  # Should handle this better but we are making some assumptions for now

        print("CAT FED", cat.name)
        food_amount = int(food_amount)
        message = f"{cat.name} has been manually fed {food_amount} units of food!"
        house.add_notification(Notifications(message, time.time()))
        flash(message)
        users = get_users_emails_from_house(house)

        date_time = datetime.fromtimestamp(time.time())
        str_time = date_time.strftime("%d-%m-%Y, %H:%M:%S")

        email(f"Cat feeding at {str_time}", message, users)
        house.events.dispense_amount = food_amount
        house.events.dispense_changed = True
        cat.daily_food = cat.daily_food + food_amount
        cat.last_fed = time.time()
        house.create()

        return redirect("/feeding")
    else:
        house = House.get(session["mac_address"])
        cats: List[Cats] = house.cats
        cat_names = [cat.name for cat in cats]
        return render_template("feeding.html", cat_names=cat_names)


@app.route("/playing", methods=["GET", "POST"])
@Authentication.login_required
def playing():
    video_key = session["mac_address"]
    return render_template(
        "playing.html", video_key=video_key, started=video_key in Camera.feeds
    )


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

    notifications = House.get(session["mac_address"]).notifications
    notifications = [(n.message, datetime.fromtimestamp(n.time).strftime("%H:%M - %B %d, %Y")) for n in notifications]
    return render_template("landing_page.html", notifications=notifications)


@app.route("/upload", methods=["POST"])
def upload_file():
    global timestamp
    mac_address = request.values.get('mac_address')

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
            assert cat is not None  # Should handle this better but we are making some assumptions for now
            TWENTY_FOUR_HOURS = 86400  # seconds in 24 hours
            ONE_MINUTE = 60


            if not cat.present and float(cat.last_visit) + ONE_MINUTE < time.time():
                cat_house.add_notification(Notifications(f"{cat.name} says hi!", time.time()))
                print("CAT VISITED", cat.name)
                cat.number_of_visits += 1
                timestamp = time.time()
                date_time = datetime.fromtimestamp(timestamp)
                str_time = date_time.strftime("%d-%m-%Y, %H:%M:%S")
                cat.last_visit = str_time

            cat.present = True

            if time.time() > float(cat.first_fed) + TWENTY_FOUR_HOURS:
                print("CAT FOOD RESET", cat.name)
                cat.daily_food = 0
                cat.first_fed = time.time()

            current_food_amount = cat.daily_food
            max_food_amount = cat.max_food
            if current_food_amount < max_food_amount and float(cat.last_fed) + Cats.FOOD_FREQUENCY < time.time():
                print("CAT FED", cat.name)
                food_amount = min(Cats.DISPENSE_AMOUNT, max_food_amount - current_food_amount)
                cat_house.add_notification(Notifications(f"{cat.name} has been fed {food_amount} units of food!", time.time()))
                users = get_users_emails_from_house(cat_house)
                date_time = datetime.fromtimestamp(timestamp)
                str_time = date_time.strftime("%d-%m-%Y, %H:%M:%S")
                email(f"Cat feeding at {str_time}", f"{cat.name} has been fed {food_amount} units of food.", users, image=image)
                cat_house.events.dispense_amount = food_amount
                cat_house.events.dispense_changed = True
                cat.daily_food = current_food_amount + food_amount
                cat.last_fed = time.time()


            cat_house.create()
        else:
            # Set all cats to not present
            cat_house: House = House.get(mac_address)
            cats: List[Cats] = cat_house.cats
            for house_cat in cats:
                house_cat.present = False
            cat_house.create()

    # We cannot save files directly after reading them or vice versa
    # file.save(filename)
    return "Success"


# A very poor way of getting the users associated with a house
def get_users_emails_from_house(house: House):
    mac_address = house.mac_address
    house_user_emails = []
    all_users = Users.ref.get()
    for user in all_users:
        user = user.to_dict()
        if user["mac_address"] == mac_address:
            house_user_emails.append(user["email"])

    return house_user_emails


@app.route("/stream", methods=["POST"])
@Authentication.login_required
def stream():
    # TODO
    return "Success"


@app.route("/clear_notifications", methods=["POST"])
@Authentication.login_required
def clear_notifications():
    house = House.get(session["mac_address"])
    house.clear_notifications()
    house.create()

    return redirect("/")


def gen(camera: Camera):
    while True:
        frame = camera.get_frame()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/video_feed")
@Authentication.login_required
def video_feed():
    video_key = session["mac_address"]
    return Response(gen(Camera(video_key)), mimetype="multipart/x-mixed-replace; boundary=frame")


def email(subject, body, recipients, image=None):
    if image is not None:
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = "crazycatcaretaker123@gmail.com"
        message['To'] = ', '.join(recipients)
        html_part = MIMEText(body)
        message.attach(html_part)
        message.attach(MIMEImage(image))
    else:
        message = MIMEText(body)
        message['Subject'] = subject
        message['From'] = "crazycatcaretaker123@gmail.com"
        message['To'] = ', '.join(recipients)

    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login("crazycatcaretaker123@gmail.com", "wklhkcqzccnkgsvr")
    smtp_server.sendmail("crazycatcaretaker123@gmail.com", recipients, message.as_string())
    smtp_server.quit()


@app.route("/send_email", methods=["GET", "POST"])
def send_email():
    subject = "Test"
    body = "This is a test"
    recipients = ["crazycatcaretaker123@gmail.com"]

    return email(subject, body, recipients)


@app.route("/view_profiles", methods=["GET"])
@Authentication.login_required
def cat_profiles():
    house: House = House.get(session["mac_address"])
    return render_template("view_profiles.html", cats=house.cats)


@app.route("/add_cat", methods=["GET", "POST"])
@Authentication.login_required
def add_cat():
    house: House = House.get(session["mac_address"])
    if request.method == 'POST':
        cat_name = request.form.get("cat-name")
        max_food = request.form.get("max-food")
        new_cat = Cats(cat_name, max_food, 0, 0, 0, 0, 0, False)
        house.add_cat(new_cat)
        house.create()
        flash(f"Cat {new_cat} added to your home")
        return redirect("/view_profiles")
    else:
        return render_template("add_cat.html")


@app.route("/register_device", methods=["POST"])
def register_device():
    mac_address = request.values.get("mac_address")
    if House.get(mac_address) is None:
        new_event = HomeEvents("OFF", False, 0, False)
        new_home = House(mac_address, [], new_event, [])
        new_home.create()
        print(f"New device registered with mac address {mac_address}")
    return "Success"
