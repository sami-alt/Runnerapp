from flask import Flask
from flask import abort, render_template, request, redirect, session, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import db
import config
import secrets

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    user = session.get('user_id')
    profile_picture = None
    stats_all = None
    my_stats = None
    my_runs = []
    stats_all = show_statistics()
    all_runs = db.query("select * from runs order by run_id limit 3")
    if user:
        user = db.query("select * from users where id = ?",[session["user_id"]], True)
        profile_picture = db.query("select image from profile_pictures where owner_id = ?",[session["user_id"]])
        my_runs = db.query("select * from runs where run_id = ? order by run_id limit 3", [session["user_id"]])
        my_stats = show_my_statistics()
    return render_template("index.html", user=user, profile_picture=profile_picture, stats_all=stats_all, my_stats=my_stats, my_runs=my_runs, all_runs=all_runs)    

#Login, logout and csrf/rigths checks
@app.route("/login_page")
def login_page():
    return render_template("login.html")

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
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    del session["csrf_token"]
    return redirect("/")

@app.route("/add")
def add():
    return render_template("add.html")

#user spesific run functions
@app.route("/add_new", methods=["POST"])
def add_new():
        require_login()
        check_csrf()
        runner_id = session["user_id"]
        name = request.form["name"]
        length = request.form["length"]
        time = request.form["time"]
        comment = request.form["comment"]
        radio_option = request.form["situation"]
        check_options = request.form.getlist("method")
        
        last_id = db.execute("insert into runs (name, length, time, comment, runner_id) values (?,?,?,?,?)", [name, length, time, comment, runner_id])
        db.execute("insert into runSituation(situation, run_id) values (?,?)", [radio_option, last_id])

        for option in check_options:
            db.execute("INSERT INTO run_in_types(run_id, type_id) values (?,?)", [last_id, int(option)])
        
        
        file = request.files["image"]
        if not file.filename.endswith(".jpg"):
            flash("Väärä tiedosto muoto!")
        image = file.read()
        if len(image) > 100 * 1024:
            flash("Liian suuri kuva!")
        
        user_id = session["user_id"]

        db.execute("insert into maps(run_id, owner_id, image) values (?,?,?)",[last_id, user_id, image])
        
        
        return redirect("/runs")

@app.route("/remove_run/<int:run_id>", methods=["GET" ,"POST"])
def remove_run(run_id):
    require_login()
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
        check_csrf()
        name = request.form["name"]
        length = request.form["length"]
        time = request.form["time"]
        comment = request.form["comment"]
        db.execute("update runs set name=?, length=?, time=?, comment=? where run_id=?",[name, length, time, comment, run_id])
        file = request.files["image"]
        if not file.filename.endswith(".jpg"):
            flash("Väärä tiedosto muoto!")
        image = file.read()
        if len(image) > 100 * 1024:
            flash("Liian suuri kuva!")
        
        user_id = session["user_id"]

        is_image = db.query("select image from maps where run_id = ?",[run_id],True )

        if not is_image:
            db.execute("insert into maps(run_id, owner_id, image) values (?,?,?)",[run_id, user_id, image])
        else:
            db.execute("update maps set image = ? where run_id = ?", [image, run_id])
        
    
    return redirect("/")

@app.route("/comment/<int:run_id>", methods=["GET", "POST"])
def guest_comment(run_id):
    require_login()
    if request.method == "GET":
        return render_template("comment.html", run=run_id)

    if request.method == "POST":
        print("trying to comment", run_id)
        check_csrf()
        comment = request.form["guest_comment"]
        db.execute("insert into comments (comment_creator, run_id, comment) values (?,?,?)", [session["user_id"], run_id, comment]) 
    return redirect("/")

#user creation
@app.route("/create_user")
def new_user():
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

#general run data availabe without user rights
@app.route("/runs")
def runs():
    names_from_db = db.query("select username, id from users")
    
    usernames = []
    i = 0
    while i < len(names_from_db):
        usernames.append((names_from_db[i][0], names_from_db[i][1]))
        i += 1

    runs = db.query("select * from runs")
    return  render_template("runs.html", runs=runs, usernames=usernames)

@app.route("/run/<int:run_id>", methods=["GET"])
def run(run_id):
    run = db.query("select * from runs where run_id = ?", [run_id], True)
    query = db.query("select comment from comments where run_id = ?",[run_id])

    comments = [dict(row) for row in query]

    return render_template("run.html", run=run, comments=comments)

@app.route("/search")
def search_window():
    return render_template("search.html")

@app.route("/search_runs", methods=["GET"])
def search():
    description = request.args.get("description")
    radio_option = request.args.get("situation")
    check_options = request.args.getlist("method")
    if description:
        like = "%"+description+"%"
        results = db.query("select r.run_id, r.name, r.length, r.time, r.comment, r.runner_id from runs r left join comments c on c.comment_creator = r.run_id where c.comment like ? or r.comment like ? or r.name like ?", [like, like, like])
        runs = [dict(row) for row in results]
    if radio_option:
        results = db.query("select r.run_id, r.name, r.length, r.time, r.comment, r.runner_id from runs r left join runSituation s on s.run_id = r.run_id where s.situation = ?",[radio_option])
        runs = [dict(row) for row in results]
    if check_options:
        runs =  []
        for option in check_options:
            temp = []
            results = db.query("""SELECT r.run_id, r.name,r.length,r.time,r.comment,r.runner_id,t.method AS run_type FROM runs r JOIN run_in_types i ON r.run_id = i.run_id JOIN types t ON t.id = i.type_id WHERE t.id = ?""", [option])
            temp = [dict(row) for row in results]
            runs.extend(temp)
    return render_template("runs.html", runs=runs)

#statistics
def show_my_statistics():
    run_data = db.query("select * from runs where runner_id = ?",[session["user_id"]])
    stats = {}


    result = [dict(stats) for stats in run_data]

    meters = 0
    longest = 0
    minutes = 0
    longest_minutes = 0

    for stat in result:
        meters += int(stat["length"])
        minutes += int(stat["time"])
        if longest < int(stat["length"]):
            longest = int(stat["length"])
        if longest_minutes < int(stat["time"]):
            longest_minutes = int(stat["time"])

    stats["runs"] = len(run_data)
    stats["all_meters"] = meters
    stats["longest_run"] = longest
    stats["longest_minutes"] = longest_minutes
    stats["all_minutes"] = minutes
    return stats

@app.route("/stats")
def show_statistics():
    run_data = db.query("select * from runs")
    users_data = db.query("select * from users")
    result = [dict(row) for row in run_data]
    stats = {}

    meters = 0
    longest = 0
    minutes = 0
    longest_minutes = 0

    for stat in result:
        meters += int(stat["length"])
        minutes += int(stat["time"])
        if longest < int(stat["length"]):
            longest = int(stat["length"])
        if longest_minutes < int(stat["time"]):
            longest_minutes = int(stat["time"])



    stats["runs"] = len(run_data)
    stats["users"] = len(users_data)
    stats["all_meters"] = meters
    stats["longest_run"] = longest
    stats["longest_minutes"] = longest_minutes
    stats["all_minutes"] = minutes

    return stats #render_template("stats.html", stats=stats)

#picture funcs

@app.route("/image_map/<int:run_id>")
def show_map(run_id):
    image = db.query("select image from maps where run_id = ?", [run_id])
    response = make_response(bytes(image[0][0]))
    response.headers.set("Content-Type", "image/png")
    return response

@app.route("/image_profile/<int:user_id>")
def show_profile_pic(user_id):
    image = db.query("select image from profile_pictures where owner_id = ?", [user_id])
    response = make_response(bytes(image[0][0]))
    response.headers.set("Content-Type", "image/png")
    return response

def update_image(user_id, image):
    excists = db.query("select * from profile_pictures where owner_id = ?", [user_id])
    if excists:
        db.execute("update profile_pictures set image = ? where owner_id = ?",[image, user_id])
    else:
        db.execute("insert into profile_pictures(image,owner_id) values (?,?)",[image, user_id])


@app.route("/add_profile_pic", methods=["GET","POST"])
def add_profile_pic():
    if request.method == "GET":
        return render_template("add_image.html")

    if request.method == "POST":
        file = request.files["image"]
        if not file.filename.endswith(".png"):
            flash("Väärä tiedosto muoto!")
            #return render_template("add_image.html")
        image = file.read()
        if len(image) > 100 * 1024:
            flash("Liian suuri kuva!")
            #return render_template("add_image.html")
        user_id = session["user_id"]
        update_image(user_id, image)
    return redirect("/")
