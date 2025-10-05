from flask import Flask
from flask import abort, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import db
import config
import secrets

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    print(session)
    return render_template("index.html")    

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    try:
        user = db.query("select * from users where username = ?" ,[username], True)
    except IndexError:
        return f"No user by {username}"
    if not user:
        return f"Ei käyttäjää nimellä {username}"
    if check_password_hash(user["password_hash"], password):
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")
    else:
        return render_template("forbidden.html")
    
def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    print("form",request.form["csrf_token"],"session", session["csrf_token"])
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.route("/logout")
def logout():
    del session["user_id"]
    return redirect("/")

@app.route("/add")
def add():
    return render_template("add.html")

@app.route("/add_new", methods=["POST"])
def add_new():
        require_login()
        check_csrf()
        runner_id = session["user_id"]
        name = request.form["name"]
        length = request.form["length"]
        time = request.form["time"]
        comment = request.form["comment"]
        db.execute("insert into runs (name, length, time, comment, runner_id) values (?,?,?,?,?)", [name, length, time, comment, runner_id])
        return redirect("/runs")

@app.route("/remove_run/<int:run_id>", methods=["GET" ,"POST"])
def remove_run(run_id):
    require_login()
    print("Run id",run_id)
    if request.method == "GET":
        return render_template("remove.html", run_id=run_id)

    if request.method == "POST":
        try:
            db.execute("delete from runs where run_id = ?", [run_id])
        except IndexError:
            return "Run could not be removed"
    return redirect("/")

@app.route("/modify_run/<int:run_id>", methods=["GET", "POST"])
def modify_run(run_id):
    require_login()
    
    run = db.query("select * from runs where run_id = ?", [run_id], True)
    if request.method == "GET":
        return render_template("modify.html", run=run)
    
    if request.method == "POST":
        name = request.form["name"]
        length = request.form["length"]
        time = request.form["time"]
        comment = request.form["comment"]
        db.execute("update runs set name=?, length=?, time=?, comment=? where run_id=?",[name, length, time, comment, run_id])
    return redirect("/")

@app.route("/create_user")
def uusi_kayttaja():
    return render_template("create_user.html")

@app.route("/add_user", methods=["POST"])
def add_user():
    username = request.form["username"]
    password = request.form["password"]
    password2 = request.form["password2"]
    if not username or not password or not password2:
        return "Textfields cannot be empty"
    if password != password2:
        return "Passwords do not match!"
    password_hash = generate_password_hash(password)
    try:
        db.execute("insert into users (username, password_hash) values (?,?)", [username, password_hash])
    except sqlite3.IntegrityError:
        return "Käyttäjänimi on jo varattu"
    return redirect("/")

@app.route("/runs")
def runs():
    runs = db.query("select * from runs")
    return  render_template("runs.html", runs=runs)

@app.route("/search")
def search_window():
    return render_template("search.html")

@app.route("/search_one", methods=["GET"])
def search():
    name = request.args.get("name")
    try:
        run = db.query("select * from runs where name = ?", [name], True)
    except  IndexError:
        return f"No run by paramameter {name}"
    return render_template("run.html", run=run)

@app.route("/stats")
def show_statistics():
    run_data = db.query("select * from runs")
    users_data = db.query("select * from users")

    stats = {}

    meters = 0
    longest = 0
    minutes = 0
    longes_minutes = 0

    i = 0
    while i < len(run_data):
        run_len = int(run_data[i]["length"])
        time = int(run_data[i]["time"])
        if run_len > longest:
            longest = run_len
        if time > longes_minutes:
            longes_minutes = time
        meters += run_len
        minutes += time
        i += 1

    stats["runs"] = len(run_data)
    stats["users"] = len(users_data)
    stats["all_meters"] = meters
    stats["longest_run"] = longest
    stats["longest_minutes"] = longes_minutes
    stats["all_minutes"] = minutes

    return render_template("stats.html", stats=stats)


@app.route("/comment/<int:run_id>", methods=["GET", "POST"])
def guest_comment(run_id):
    require_login()

    if request.method == "GET":
        return render_template("comment.html", run=run_id)

    if request.method == "POST":
        comment = request.form["guest_comment"]
        db.execute("update runs set guest_comment = ? where run_id = ?", [comment, run_id]) 
    return redirect("/")