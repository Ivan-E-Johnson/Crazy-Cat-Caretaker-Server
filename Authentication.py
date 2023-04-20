import pyrebase
import requests
from Home import Users, House, Cats, DatabaseObject
from flask import session, redirect, flash
from functools import wraps

AUTH_CONFIG = {
    "apiKey": "AIzaSyBx6ut501XQhSePVu7Fi8SbhfYMuOAD344",
    "authDomain": "testingccc-3b63d.firebaseapp.com",
    "databaseURL": "https://testingccc-3b63d-default-rtdb.firebaseio.com",
    "projectId": "testingccc-3b63d",
    "storageBucket": "testingccc-3b63d.appspot.com",
    "messagingSenderId": "1031446491621",
    "appId": "1:1031446491621:web:971d8fff08ce27a547bf0c",
    "measurementId": "G-M1PX452PG9",
}

################################################################
# AUTHENTICATION
firebase = pyrebase.initialize_app(AUTH_CONFIG)
auth = firebase.auth()
################################################################

def create_user(email, password, mac_address):
    house = House.get(mac_address)
    if house is None:
        flash(f"Could not find a registered device with a mac address of {mac_address}")
        return False
    try:
        user = auth.create_user_with_email_and_password(email, password)
        Users(email, mac_address).create()
    except requests.exceptions.HTTPError as e:
        flash(f"User creation failed: {e}")
        return False
    flash(f"Created New User: {email}!")
    login(email, password)
    return True


def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        user_db: Users = Users.get(email)
    except requests.exceptions.HTTPError as e:
        flash(f"Log in failed: {e} {type(e)} {e.request}")
        return None
    flash(f"Signed in as {email}!")
    session["user"] = user
    session["mac_address"] = user_db.mac_address
    return user


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwds):
        print("WE GOT HERE")
        if "user" in session:
            return func(*args, **kwds)
        else:
            return redirect("/login")
    return wrapper


if __name__ == "__main__":
    firebase = pyrebase.initialize_app(AUTH_CONFIG)
    auth = firebase.auth()

    email = "teat@test.com"
    password = "123456"

    user = auth.create_user_with_email_and_password(email, password)  # want ID token
    print(user)
    # user = auth.sign_in_with_email_and_password(email,password)
    # print(user)

    info = auth.get_account_info(user["idToken"])
    print(info)
