from flask import Flask, render_template, flash, request, redirect, abort

app = Flask(__name__)
app.config.from_envvar("APPLICATION_SETTINGS")


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


@app.route('/upload', methods=['POST'])
def upload_file():
    print(request)
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return "No file received", 400

    file = request.files['file']

    return "Success"
