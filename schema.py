import sqlite3

connection = sqlite3.connect('database.db')

cursor = connection.cursor()

cursor.execute("pragma foreign_keys = on")

schema_queries = [
    '''create table if not exists user (
        user_id integer primary key autoincrement,
        username text,
        email text,
        fullname text,
        password_hash text,
        role text,
        joining_date text,
        wallet_id integer,
        foreign key (wallet_id) references wallet(wallet_id)
    )''',
    '''create table if not exists admin (
        admin_id integer primary key autoincrement,
        user_id integer,
        foreign key (user_id) references user(user_id)
    )''',
    '''create table if not exists trainer (
        trainer_id integer primary key autoincrement,
        specializes_in text,
        experience integer,
        weight real,
        award text,
        height real,
        user_id integer,
        verified text,
        foreign key (user_id) references user(user_id)
    )''',
    '''create table if not exists member (
        member_id integer primary key autoincrement,
        target text,
        height real,
        weight real,
        take_goal real,
        burn_goal real,
        user_id integer,
        foreign key (user_id) references user(user_id)
    )''',
    '''create table if not exists exercise (
        exercise_id integer primary key autoincrement,
        exercise_detail text,
        sets integer,
        reps integer,
        calorie_burn integer
    )''',
    '''create table if not exists food (
        food_id integer primary key autoincrement,
        food_detail text,
        quantity text,
        calorie_gain integer
    )''',
    '''create table if not exists wallet (
        wallet_id integer primary key autoincrement,
        balance real
    )''',
    '''create table if not exists recharge (
        recharge_id integer primary key autoincrement,
        amount real,
        timestamp text,
        status text,
        user_id integer,
        foreign key (user_id) references user(user_id)
    )''',
    '''create table if not exists post (
        post_id integer primary key autoincrement,
        post_body text,
        user_id integer,
        author text,
        creation_time text,
        tag text,
        foreign key (user_id) references user(user_id)
    )''',
    '''create table if not exists comment (
        comment_id integer primary key autoincrement,
        comment_body text,
        posting_time text,
        user_id integer,
        post_id integer,
        foreign key (user_id) references user(user_id),
        foreign key (post_id) references post(post_id)
    )''',
    '''create table if not exists health_info (
        member_id integer,
        disease text,
        diagnosed text,
        foreign key (member_id) references member(member_id)
    )''',
    '''create table if not exists exercise_info (
        exercise_id integer,
        member_id integer,
        timestamp text,
        foreign key (exercise_id) references exercise(exercise_id),
        foreign key (member_id) references member(member_id)
    )''',
    '''create table if not exists diet_info (
        diet_id integer primary key autoincrement,
        food_id integer,
        member_id integer,
        timestamp text,
        foreign key (food_id) references food(food_id),
        foreign key (member_id) references member(member_id)
    )''',
    '''create table if not exists verification (
        admin_id integer,
        trainer_id integer,
        foreign key (admin_id) references admin(admin_id),
        foreign key (trainer_id) references trainer(trainer_id)
    )''',
    '''create table if not exists payment (
        payment_id integer primary key autoincrement,
        admin_id integer,
        trainer_id integer,
        amount real,
        foreign key (admin_id) references admin(admin_id),
        foreign key (trainer_id) references trainer(trainer_id)
    )''',
    '''create table if not exists training_session (
        session_id integer primary key autoincrement,
        trainer_id integer,
        member_id integer,
        session_length integer,
        is_complete text,
        foreign key (trainer_id) references trainer(trainer_id),
        foreign key (member_id) references member(member_id)
    )''',
    '''create table if not exists reviews (
        member_id integer,
        trainer_id integer,
        review text,
        rating integer,
        foreign key (member_id) references member(member_id),
        foreign key (trainer_id) references trainer(trainer_id)
    )'''
]

for query in schema_queries:
    cursor.execute(query)

connection.close()
