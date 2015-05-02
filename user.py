from dbhelper import *
import email_helper
import string
import random
import sqlite3
import smtplib
import datetime
from flask import current_app as app
from flask import url_for, render_template
from itsdangerous import URLSafeSerializer
from werkzeug.security import generate_password_hash, check_password_hash

# Constants
SELECT_QUERY = "SELECT * FROM users WHERE username=?"
SELECT_BY_EMAIL_QUERY = "SELECT * FROM users WHERE email=?"
SELECT_BY_PW_RESET_QUERY = "SELECT * FROM users WHERE pw_reset=?"
SELECTALL_QUERY = "SELECT * FROM users"
UPDATE_PW_RESET_QUERY = "UPDATE users SET pw_reset=? WHERE id=?"
ACTIVATE_QUERY = "UPDATE users SET active=1 WHERE username=?"
API_KEY_QUERY = "UPDATE users SET api_key=? WHERE id=?"
ME = "nobody@acm.cs.purdue.edu"

class UserNotFoundError(Exception):
    pass

class User:
    def __init__(self, user):
        self.user_id = user[USER_INDEX_COLUMN]
        self.api_key = user[USER_API_KEY_COLUMN] or self.generate_api_key()
        self.username = user[USER_USERNAME_COLUMN]
        self.pw_hash = user[USER_PASSWORD_COLUMN]
        self.email = user[USER_EMAIL_COLUMN]
        self.display = user[USER_DISPLAY_COLUMN]
        self.active = user[USER_ACTIVE_COLUMN]
        self.is_admin = user[USER_ADMIN_COLUMN]
        self.pw_reset_key = user[USER_PW_RESET_COLUMN]

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return not self.is_authenticated()

    def is_active(self):
        return self.active

    def is_administrator(self):
        return self.is_admin

    def get_id(self):
        return self.username

    def get_user_id(self):
        return self.user_id

    def get_api_key(self):
        return self.api_key

    def get_username(self):
        return self.username

    def get_email(self):
        return self.email

    def get_display(self):
        return self.display

    def get_pw_reset_key(self):
        return self.pw_reset_key

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def set_active(self):
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        data = (self.username, )
        c.execute(ACTIVATE_QUERY, data)
        conn.commit()
        conn.close()

    def generate_api_key(self):
        chars = string.ascii_lowercase + string.digits
        api_key = ''.join(random.choice(chars) for _ in range(12))
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        data = (api_key, self.get_user_id(), )
        c.execute(API_KEY_QUERY, data)
        conn.commit()
        conn.close()

        self.api_key = api_key

    def send_activation_email(self):
        s = URLSafeSerializer(app.config['SECRET_KEY'])
        payload = s.dumps(self.username)
        url = url_for('activate', payload=payload, _external=True)

        subject = "Activate your account"
        text = render_template("activate.txt", url=url)
        html = render_template("activate.html", url=url)
        email_helper.send_email(self.get_email(), subject, text, html)

    def send_pw_reset_email(self):
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        reset_link = self.get_display() + str(datetime.datetime.now())
        reset_link_hashed = User.get_pw_hash(reset_link)
        data = (reset_link_hashed, self.get_user_id(), )
        c.execute(UPDATE_PW_RESET_QUERY, data)
        conn.commit()
        conn.close()

        url = url_for('forgot', payload=reset_link_hashed, _external=True)

        subject = "Password reset email for ACM Poker"
        text = render_template("pw_reset.txt", user=self, url=url)
        html = render_template("pw_reset.html", user=self, url=url)
        email_helper.send_email(self.get_email(), subject, text, html)

    def print_debug(self):
        return """
            <h3>Username: {}</h3>
            <h3>Email: {}</h3>
            <h3>Display: {}</h3>
            <h3>Active: {}</h3>
            <h3>Admin: {}</h3>
        """.format(self.username, self.email, self.display, self.active, self.is_admin)

    @classmethod
    def get(self_class, username):
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        data = (username, )
        c.execute(SELECT_QUERY, data)
        user = c.fetchone()
        conn.close()

        try:
            if user is None:
                raise UserNotFoundError
            return User(user)
        except UserNotFoundError:
            return None

    @classmethod
    def get_by_email(self_class, email):
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        data = (email, )
        c.execute(SELECT_BY_EMAIL_QUERY, data)
        user = c.fetchone()
        conn.close()
        try:
            if user is None:
                raise UserNotFoundError
            return User(user)
        except UserNotFoundError:
            return None

    @classmethod
    def get_by_pw_reset_key(self_class, pw_reset_key):
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        data = (pw_reset_key, )
        c.execute(SELECT_BY_PW_RESET_QUERY, data)
        user = c.fetchone()
        conn.close()
        try:
            if user is None:
                raise UserNotFoundError
            return User(user)
        except UserNotFoundError:
            return None

    @classmethod
    def getall(self_class):
        users = []
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        for row in c.execute(SELECTALL_QUERY):
            users.append(User(row))
        conn.close()
        return users

    @classmethod
    def get_pw_hash(self_class, password):
        return generate_password_hash(password)
