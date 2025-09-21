from flask import Flask
from flask import render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
'import config'

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")    

@app.route("/login")
def kirjautumis_sivu():
    return render_template("kirjadu.html")

@app.route("/kirjaudu", methods=["POST"])
def kirjaudu():
    username = request.form["username"]
    password = request.form["password"]
    db = sqlite3.connect("database.db")
    password_hash = db.execute("select password_hash from kayttaja where username = (=)", [username])
    db.close()
    if check_password_hash(password_hash, password):
         redirect("/")
    else:
        return render_template("forbidden.html")


@app.route("/lisaa")
def uusi():
    return render_template("lisaa.html")

@app.route("/uusi", methods=["POST"])
def lisaa_uusi():
        name = request.form["name"]
        length = request.form["length"]
        time = request.form["time"]
        comment = request.form["comment"]
        db = sqlite3.connect("database.db")
        db.execute("insert into suoritukset (name, length, time, comment) values (?,?,?,?)",[name, length, time, comment])
        db.commit()
        db.close()
        return redirect("/suoritukset")

def poista_suoritus():
     return redirect("/suoritukset")

@app.route("/luo_kayttaja")
def uusi_kayttaja():
        return render_template("luo_kayttaja.html")

@app.route("/uusi_kayttaja", methods=["POST"])
def luokäyttäjä():
     username = request.form["kayttaja_nimi"]
     password = request.form["salasana"]
     password2 = request.form["salasana2"]
     if password != password2:
        return "virhe"
     password_hash = generate_password_hash(password) 
     db = sqlite3.connect("database.db")
     db.execute("insert into kayttajat (username, password_hash) values (?,?)",[username, password_hash])
     db.commit()
     db.close()
     return redirect("/")

@app.route("/suoritukset")
def suoritukset():
    db = sqlite3.connect("database.db")
    suoritukset = db.execute("select name, length, time, comment from suoritukset").fetchall()
    db.close()
    return  render_template("suoritukset.html", suoritukset=suoritukset)

'''
@app.route("/hae")
def hae():
    name = request.form["name"]
    db = sqlite3.connect("database.db")
    suoritus = db.execute("select * from suoritukset where name = ?", [name]).fetchone()
    db.close()
    return render_template("suoritus.html", suoritus=suoritus)
'''

@app.route("/haku")
def hae_suoritus():
    return render_template("haku.html")