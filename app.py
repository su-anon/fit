from flask import Flask, request, session, render_template, redirect, url_for, make_response
import datetime
import os
import requests 
import sqlite3
import schema
import bcrypt
import json

with open(".secret") as secretfile:
    secrets = json.load(secretfile)

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
                           (username, email, fullname, password_hash, role, datetime.datetime.now().isoformat(),))
        userid = connection.execute("select user_id from user where user.username=?", (username,)).fetchone()[0]
        cursor = connection.execute("insert into wallet (balance) values (?)", (0,))
        wallet_id = cursor.lastrowid
        connection.execute("update user set wallet_id=? where user_id=?", (wallet_id, userid))

    return userid

def get_leaderboard():
    with sqlite3.connect(DB_NAME) as connection:
        gain_leaderboard = connection.execute("""
                                              select username, sum(food.calorie_gain) as gain
                                              from
                                              diet_info
                                              left join food on food.food_id=diet_info.food_id
                                              left join member on member.member_id=diet_info.member_id
                                              left join user on user.user_id=member.user_id
                                              where date(timestamp)=date('now', 'localtime')
                                              group by username
                                              order by gain desc
                                              limit 10 offset 0
                                              """).fetchall()
        burn_leaderboard = connection.execute("""
                                              select username, sum(exercise.calorie_burn) as burn
                                              from
                                              exercise_info
                                              left join exercise on exercise.exercise_id=exercise_info.exercise_id
                                              left join member on member.member_id=exercise_info.member_id
                                              left join user on user.user_id=member.user_id
                                              where date(timestamp)=date('now', 'localtime')
                                              group by username
                                              order by burn desc
                                              limit 10 offset 0
                                              """).fetchall()
        return gain_leaderboard, burn_leaderboard

def get_balance(user_id):
    with sqlite3.connect(DB_NAME) as connection:
        user_id = str(user_id)
        connection.row_factory = sqlite3.Row
        balance = connection.execute("select balance from wallet left join user on user.wallet_id=wallet.wallet_id where user_id=?", (user_id),).fetchone()["balance"]
        return balance





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
        with sqlite3.connect(DB_NAME) as connection:
            connection.row_factory = sqlite3.Row
            member_id = session.get("member_id")
            gain = connection.execute("select sum(food.calorie_gain) as gain from diet_info left join food on food.food_id=diet_info.food_id where date(timestamp)=date('now', 'localtime') and member_id=?", (member_id,)).fetchone()["gain"] or 0
            burn = connection.execute("select sum(exercise.calorie_burn) as burn from exercise_info left join exercise on exercise.exercise_id=exercise_info.exercise_id where date(timestamp)=date('now', 'localtime') and member_id=?", (member_id,)).fetchone()["burn"] or 0
            member_details = connection.execute("select take_goal, burn_goal from member where member_id=?", (member_id,)).fetchone()
            burn_goal, take_goal = member_details["burn_goal"], member_details["take_goal"]
            gain_leaderboard, burn_leaderboard = get_leaderboard()
            balance = get_balance(session.get("user_id"))
            return render_template("home-member.html", gain=gain, burn=burn, take_goal=take_goal, burn_goal=burn_goal, gain_leaderboard=gain_leaderboard, burn_leaderboard=burn_leaderboard, balance=balance)

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
        BMR = 10*float(weight) + 6.25*float(height) - 120
        take_goal = int(BMR*1.55)
        burn_goal = int(take_goal*0.25)
        with sqlite3.connect(DB_NAME) as connection:
            connection.execute("insert into member (target, height, weight, take_goal, burn_goal, user_id) values (?, ?, ?, ?, ?, ?)", (target, height, weight, take_goal, burn_goal, userid))
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

@app.route("/approve/<int:trainer_id>", methods=["POST"])
def approve_trainer(trainer_id):
    with sqlite3.connect(DB_NAME) as connection:
        connection.execute("update trainer set verified='verified' where trainer_id=?", (trainer_id,))
        name, = connection.execute("select username from trainer left join user on trainer.user_id=user.user_id where trainer_id=?", (trainer_id,)).fetchone()
    return f'<div class="bg-green-100 text-green-800 p-4 rounded-lg shadow">✅ Trainer @{name} has been approved.</div>'

@app.route("/reject/<int:trainer_id>", methods=["POST"])
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
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        foods = [{"id": food["food_id"], "detail": food["food_detail"], "quantity": food["quantity"], "calories": food["calorie_gain"]} for food in connection.execute("select * from food").fetchall()]
        exercises = [{"id": exercise["exercise_id"], "detail": exercise["exercise_detail"], "sets": exercise["sets"], "reps": exercise["reps"], "calories": exercise["calorie_burn"]} for exercise in connection.execute("select * from exercise").fetchall()]

    return render_template("record.html", diets=foods, workouts = exercises)

@app.route("/add-record", methods=["POST"])
def add_record():
    if not session.get("username") or not session.get("member_id"):
        response = make_response("", 204)
        response.headers["HX-Redirect"] = url_for("login")
        return response
    record_type = request.form.get("type")
    item = request.form.get("item")
    with sqlite3.connect(DB_NAME) as connection:
        member_id = session.get("member_id")
        if record_type=="diet":
            connection.execute("insert into diet_info (food_id, member_id, timestamp) values (?, ?, ?)", (item, member_id, datetime.datetime.now().isoformat()))
        elif record_type=="exercise":
            connection.execute("insert into exercise_info (exercise_id, member_id, timestamp) values (?, ?, ?)", (item, member_id, datetime.datetime.now().isoformat()))

    get_leaderboard()
    return '<span class="text-sm text-green-600">Added</span>'

@app.route("/wallet")
def wallet():
    balance = get_balance(session.get("user_id"))
    return render_template("wallet.html", balance=balance)

@app.route("/payment", methods=["POST"])
def payment():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    amount = request.form.get("amount")
    with sqlite3.connect(DB_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute("insert into recharge (amount, timestamp, status, user_id) values (?, ?, ?, ?)", (str(amount), datetime.datetime.now().isoformat(), "pending", str(session.get("user_id"))))
        recharge_id = cursor.lastrowid
    post_data = {
        "store_id": secrets.get("store_id"),
        "store_passwd": secrets.get("store_passwd"),
        "total_amount": amount,
        "currency": "BDT",
        "tran_id": recharge_id,
        "success_url": request.host_url + "success",
        "fail_url": request.host_url + "fail",
        "cancel_url": request.host_url + "cancel",
        "cus_name": session.get("username"),
        "cus_email": "member@fitnesspro",
        "cus_add1": "Dhaka",
        "cus_phone": "01000000000",
        "shipping_method": "NO",
        "product_name": "Payment",
        "product_category": "Payment",
        "product_profile": "general",
        "cus_city":"Dhaka",
        "cus_country":"Bangladesh",
    }

    response = requests.post(secrets.get("init_url"), data=post_data)
    response_data = response.json()
    if response_data["status"] == "SUCCESS":
        return redirect(response_data["GatewayPageURL"])
    else:
        return "Payment initiation failed: " + response_data.get("failedreason", "Unknown error")

@app.route("/success", methods=["POST"])
def success():
    val_id = request.form["val_id"]
    data = {"val_id":val_id, "store_id":secrets.get("store_id"), "store_passwd": secrets.get("store_passwd"), "format":"json"}
    res = requests.get(secrets.get("valid_url"), params=data)
    if res.json().get("status")=="VALID":
        recharge_id = res.json().get("tran_id")
        amount = res.json().get("store_amount")
        with sqlite3.connect(DB_NAME) as connection:
            connection.execute("update recharge set status=? where recharge_id=?", (val_id, recharge_id))
            connection.execute("update wallet set balance=balance+?", (amount,))
        return redirect(url_for("wallet")+"?msg=✅ Payment Successful")
    else:
        return redirect(url_for("wallet")+"?msg=❌ FRAUD!!!")
        return ""

@app.route("/fail", methods=["POST"])
def fail():
    return redirect(url_for("wallet")+"?msg=❌ Payment Failed")

@app.route("/cancel", methods=["POST"])
def cancel():
    return redirect(url_for("wallet")+"?msg=🚫 Payment Cancelled")

@app.route("/forum", methods=["GET", "POST"])
def forum():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        tag = request.form.get("tag")
        user_id = session.get("user_id")
        author = session.get("username", "Anonymous")
        with sqlite3.connect(DB_NAME) as connection:
            connection.execute("insert into post (post_body, user_id, author, creation_time, tag) values (?, ?, ?, ?, ?)", (content, user_id, author, datetime.datetime.now().isoformat(), tag))
        return redirect(url_for("forum"))
    if request.method == "GET":
        with sqlite3.connect(DB_NAME) as connection:
            connection.row_factory = sqlite3.Row
            posts = connection.execute("select * from post order by creation_time limit 10 offset 0").fetchall()
        return render_template("forum.html", posts=posts)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__=="__main__":
    # app.secret_key = os.urandom(12)
    app.secret_key = "appsecret"
    app.run(debug=True, host="0.0.0.0")
