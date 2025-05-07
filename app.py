from flask import Flask, request, session, render_template, redirect, url_for
import datetime
import os
import requests 
import sqlite3
import schema
import bcrypt

app = Flask(__name__)

DB_NAME = "database.db"

def username_exists(username):
    with sqlite3.connect(DB_NAME) as connection:
        return bool(connection.execute("select * from user where user.username=?", (username,)).fetchall())

def email_exists(email):
    with sqlite3.connect(DB_NAME) as connection:
        return bool(connection.execute("select * from user where user.email=?", (email,)).fetchall())

def create_user(username, email, fullname, password, role):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt());
    with sqlite3.connect(DB_NAME) as connection:
        connection.execute("insert into user (username, email, fullname, password_hash, role, joining_date) values (?, ?, ?, ?, ?, ?)",
                           (username, email, fullname, password_hash, role, datetime.datetime.now(),))
    return None

@app.route("/", methods=["GET"])
def index():
    if session.get("user_id"):
        return render_template("home.html", username=session['username'])

    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method=="GET":
        return render_template("register.html")

    if request.method=="POST":
        username = request.form.get("username")
        if username_exists(username):
            return render_template("register.html", error="Username exists!")

        email = request.form.get("email")
        if email_exists(email):
            return render_template("register.html", error="Email exists!")

        fullname = request.form.get("fullname")
        password = request.form.get("password")
        create_user(username, email, fullname, password, "MEMBER")
        return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="GET":
        if session.get("username"):
            return redirect(url_for("index", username=session.get("username")))

        return render_template("login.html")

    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        with sqlite3.connect(DB_NAME) as connection:
            hash_password = connection.execute("select password_hash from user where user.username=?", (username,)).fetchone()
            if hash_password:
                print(password)
                hash_check = bcrypt.checkpw(password.encode(), hash_password[0])
            else:
                hash_check = False
        if hash_check:
            user_id, username = connection.execute("select user_id, username from user where user.username=?", (username,)).fetchone()
            session["user_id"] = user_id
            session["username"] = username
            return redirect(url_for("index", username=username))
        else:
            return render_template("login.html", error="Wrong username or password")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__=="__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host="0.0.0.0")
