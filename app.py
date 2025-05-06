from flask import Flask, request, session, render_template, redirect, url_for
import datetime
import os
import requests 
import sqlite3
import schema
import bcrypt

app = Flask(__name__)

DB_NAME = "database.db"

@app.route("/", methods=["GET"])
def index():
    if session.get("user_id"):
        return "HOME PAGE"
    else:
        return render_template("home.html", username="Placeholder")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method=="GET":
        return render_template("register.html")
    elif request.method=="POST":
        username = request.form.get("username")
        email = request.form.get("email")
        with sqlite3.connect(DB_NAME) as connection:
            username_exists = connection.execute("select * from user where user.username=?", (username,)).fetchall()
            email_exists = connection.execute("select * from user where user.email=?", (email,)).fetchall()
            if username_exists:
                return render_template("register.html", error="Username exists!")
            elif email_exists:
                return render_template("register.html", error="Email exists!")
            else:
                password = request.form.get("password")
                password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt());
                fullname = request.form.get("fullname")
                connection.execute("insert into user (username, email, fullname, password_hash, role, joining_date) values (?, ?, ?, ?, ?, ?)", (username, email, fullname, password_hash, "MEMBER", datetime.datetime.now(),))
                return "SUCCESS"

#hash_check = bcrypt.checkpw("1".encode(), "hashed")
if __name__=="__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host="0.0.0.0")
