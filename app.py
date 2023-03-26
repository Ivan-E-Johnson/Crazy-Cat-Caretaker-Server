from flask import Flask, render_template, flash

app = Flask(__name__)
app.config.from_envvar("APPLICATION_SETTINGS")

@app.route("/")
def hello_world():
    return render_template("index.html", title="Hello")

@app.route("/login")
def login():
    flash("TEST ALERT")
    return render_template("login.html")