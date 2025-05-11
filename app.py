from flask import Flask, request, session, render_template, redirect, url_for, make_response
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
        userid = connection.execute("select user_id from user where user.username=?", (username,)).fetchone()[0]
        cursor = connection.execute("insert into wallet (balance) values (?)", (0,))
        wallet_id = cursor.lastrowid
        connection.execute("insert into user (wallet_id) values (?)",str(wallet_id))
        connection.execute("select * from user left join wallet where username=?", (username,)).fetchone()

    return userid

@app.route("/", methods=["GET"])
def index():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    
    role = session.get("role")

    if role=="ADMIN":
        with sqlite3.connect(DB_NAME) as connection:
            connection.row_factory = sqlite3.Row
            trainer_applications = connection.execute("select trainer.*, user.fullname from trainer left join user on trainer.user_id=user.user_id where verified='pending'").fetchall()
            return render_template("home-admin.html", trainers=trainer_applications)
    elif role=="TRAINER":
        return render_template("home-trainer.html")
    elif role=="MEMBER":
        return render_template("home-member.html")

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
        userid = create_user(username, email, fullname, password, "MEMBER")
        target = request.form.get("target")
        height = request.form.get("height")
        weight = request.form.get("weight")
        with sqlite3.connect(DB_NAME) as connection:
            connection.execute("insert into member (target, height, weight, user_id) values (?, ?, ?, ?)", (target, height, weight, userid))
        return redirect(url_for("login"))

@app.route("/regtrainer", methods=["GET", "POST"])
def regtrainer():
    if request.method=="GET":
        return render_template("regtrainer.html")
    if request.method=="POST":
        username = request.form.get("username")
        if username_exists(username):
            return render_template("regtrainer.html", error="Username exists!")

        email = request.form.get("email")
        if email_exists(email):
            return render_template("regtrainer.html", error="Email exists!")

        fullname = request.form.get("fullname")
        password = request.form.get("password")
        userid = create_user(username, email, fullname, password, "TRAINER")
        specializes_in = request.form.get("specializes_in")
        experience = request.form.get("experience")
        weight = request.form.get("weight")
        height = request.form.get("height")
        award = request.form.get("award")

        with sqlite3.connect(DB_NAME) as connection:
            connection.execute("insert into trainer (specializes_in, experience, weight, award, height, verified, user_id) values (?, ?, ?, ?, ?, ?, ?)", (specializes_in, experience, weight, award, height, "pending", userid))
        return redirect(url_for("login"))

@app.route('/approve/<int:trainer_id>', methods=['POST'])
def approve_trainer(trainer_id):
    with sqlite3.connect(DB_NAME) as connection:
        connection.execute("update trainer set verified='verified' where trainer_id=?", (trainer_id,))
        name, = connection.execute("select username from trainer left join user on trainer.user_id=user.user_id where trainer_id=?", (trainer_id,)).fetchone()
        print(name)
    return f'<div class="bg-green-100 text-green-800 p-4 rounded-lg shadow">✅ Trainer @{name} has been approved.</div>'

@app.route('/reject/<int:trainer_id>', methods=['POST'])
def reject_trainer(trainer_id):
    with sqlite3.connect(DB_NAME) as connection:
        connection.execute("update trainer set verified='rejected' where trainer_id=?", (trainer_id,))
        name, = connection.execute("select username from trainer left join user on trainer.user_id=user.user_id where trainer_id=?", (trainer_id,)).fetchone()
    return f'<div class="bg-red-100 text-red-800 p-4 rounded-lg shadow">❌ Trainer @{name} has been rejected.</div>'

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="GET":
        if session.get("username"):
            return redirect(url_for("index"))

        else:
            return render_template("login.html")

    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        with sqlite3.connect(DB_NAME) as connection:
            hash_password = connection.execute("select password_hash from user where user.username=?", (username,)).fetchone()
            if hash_password:
                hash_check = bcrypt.checkpw(password.encode(), hash_password[0])
            else:
                hash_check = False
        if hash_check:
            user_id, username, role = connection.execute("select user_id, username, role from user where user.username=?", (username,)).fetchone()
            session["user_id"] = user_id
            session["username"] = username
            session["role"] = role
            if role=="MEMBER":
                member_id, = connection.execute("select member_id from member where user_id=?", (user_id,)).fetchone()
                session["member_id"]=member_id
            elif role=="TRAINER":
                trainer_id, verified = connection.execute("select trainer_id, verified from trainer where user_id=?", (user_id,)).fetchone()
                if verified=="pending":
                    session.clear()
                    return "Please wait till an admin approves your application."
                elif verified=="rejected":
                    session.clear()
                    return "Your application has been rejected by the admins."
                elif verified=="verified":
                    session["trainer_id"]=trainer_id
            elif role=="ADMIN":
                admin_id, = connection.execute("select admin_id from admin where user_id=?", (user_id,)).fetchone()
                session["admin_id"]=admin_id

            return redirect(url_for("index"))

        else:
            return render_template("login.html", error="Wrong username or password")

@app.route("/record", methods=["GET", "POST"])
def record():
    if not session.get("role")=="MEMBER":
        return "Not authorized"
    if request.method=="GET":
        if not session.get("username"):
            return render_template("login.html")

    with sqlite3.connect(DB_NAME) as connection:
        cursor = connection.cursor()
        foods = [{"id":food[0], "name":food[1], "desc":f"{food[2]} · {food[3]} kcal"} for food in cursor.execute("select * from food").fetchall()]
        exercises = [{"id":exercise[0], "name":exercise[1], "desc":f"{exercise[2]} sets · {exercise[3]} reps · {exercise[4]} kcal burns"} for exercise in cursor.execute("select * from exercise").fetchall()]
    return render_template("record.html", diets=foods, workouts = exercises)

@app.route("/add-record", methods=["POST"])
def add_record():
    if not session.get("username"):
        response = make_response('', 204)
        response.headers['HX-Redirect'] = url_for("login")
        return response
    record_type = request.form.get("type")
    item = request.form.get("item")
    

    
    return '<span class="text-sm text-green-600">Added</span>'

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__=="__main__":
    # app.secret_key = os.urandom(12)
    app.secret_key = "appsecret"
    app.run(debug=True, host="0.0.0.0")
