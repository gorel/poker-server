from dbhelper import *
import string
import random
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app as app
from flask import url_for, render_template
from itsdangerous import URLSafeSerializer
from werkzeug.security import generate_password_hash, check_password_hash

# Constants
SELECT_QUERY = "SELECT * FROM users WHERE username=?"
SELECTALL_QUERY = "SELECT * FROM users"
ACTIVATE_QUERY = "UPDATE users SET active=1 WHERE username=?"
API_KEY_QUERY = "UPDATE users SET api_key=? WHERE id=?"
ME = "nobody@acm.cs.purdue.edu"

class UserNotFoundError(Exception):
    pass

class User:
    def __init__(self, user):
        self.user_id = user[USER_INDEX_COLUMN]
        self.api_key = user[USER_API_KEY_COLUMN]
        self.username = user[USER_USERNAME_COLUMN]
        self.pw_hash = user[USER_PASSWORD_COLUMN]
        self.email = user[USER_EMAIL_COLUMN]
        self.display = user[USER_DISPLAY_COLUMN]
        self.active = user[USER_ACTIVE_COLUMN]
        self.is_admin = user[USER_ADMIN_COLUMN]

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
        chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        api_key = ''.join(random.choice(chars) for _ in range(10))
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        data = (api_key, self.get_user_id(), )
        c.execute(API_KEY_QUERY, data)
        conn.commit()
        conn.close()

    def send_confirmation_email(self):
        s = URLSafeSerializer(app.config['SECRET_KEY'])
        payload = s.dumps(self.username)
        url = url_for('activate', payload=payload, _external=True)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Activate your account"
        msg['From'] = ME
        msg['To'] = self.email

        text = render_template('activate.txt', url=url)
        html = render_template('activate.html', url=url)
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        msg.attach(part1)
        msg.attach(part2)

        s = smtplib.SMTP('localhost', 9314)
        s.sendmail(ME, self.email, msg.as_string())
        s.quit()

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
