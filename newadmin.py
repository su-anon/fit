import sqlite3
import getpass
import bcrypt
import datetime

DB_NAME = "database.db"

username = input("Username: ")
email = input("Email: ")
fullname = input("Full Name: ")
password = getpass.getpass("Password: ")
role = "ADMIN"

with sqlite3.connect(DB_NAME):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt());
    with sqlite3.connect(DB_NAME) as connection:
        connection.execute("insert into user (username, email, fullname, password_hash, role, joining_date) values (?, ?, ?, ?, ?, ?)",
                           (username, email, fullname, password_hash, role, datetime.datetime.now(),))
        userid = connection.execute("select user_id from user where user.username=?", (username,)).fetchone()[0]
        cursor = connection.execute("insert into wallet (balance) values (?)", (0,))
        wallet_id = cursor.lastrowid
        connection.execute("insert into user (wallet_id) values (?)",str(wallet_id))
        userid = connection.execute("select user_id from user where user.username=?", (username,)).fetchone()[0]
        connection.execute("insert into admin (user_id) values (?)", (userid, ))
        print("Admin account created with username: " + username)
