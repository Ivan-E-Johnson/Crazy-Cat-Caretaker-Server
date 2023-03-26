from flask import Flask, render_template, flash, request, redirect

app = Flask(__name__)
app.config.from_envvar("APPLICATION_SETTINGS")

@app.route("/")
def hello_world():
    return render_template("index.html", title="Hello")

@app.route("/login", methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        flash(request.form['username'])
        return redirect("/")
    else:
        return render_template("login.html")