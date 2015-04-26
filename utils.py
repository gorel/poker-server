from user import User
import sqlite3
from flask import Flask, request, flash
from flask_bootstrap import Bootstrap
from flask.ext.appconfig import AppConfig
from flask.ext.login import LoginManager, login_user, logout_user

# Constants
CONFIG_FILE = 'config.py'
INSERT_QUERY = "INSERT INTO users ('username', 'password') VALUES(?, ?)"

# Login Manager creation function
def create_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"
    return login_manager

# App creation function
def create_app(name='app', configfile=CONFIG_FILE):
    app = Flask(name)
    Bootstrap(app)
    AppConfig(app, configfile)
    return app

def do_login():
    username = request.form['username']
    password = request.form['password']
    remember = request.form['remember']

    user = User.get(username)
    if user and user.check_password(password):
        login_user(user, remember=remember)
        return None
    elif user:
        return 'Incorrect password'
    else:
        return 'Unknown username'

def do_register():
    username = request.form['username']
    password = request.form['password']
    confirm  = request.form['confirm']
    user = User.get(username)

    if password != confirm:
        return 'Passwords do not match'
    elif user and user.check_password(password):
        login_user(user)
        return None
    elif user:
        return 'Username already in use'
    else:
        add_user_to_db(username, password)
        return None

def add_user_to_db(username, password):
    # First salt and hash the password
    pw_hash = User.get_pw_hash(password)

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    data = (username, pw_hash, )
    c.execute(INSERT_QUERY, data)
    conn.commit()
    conn.close()

def do_admin_actions():
    pass

def render_json(posted=False):
    key = request.args.get('key', None)
    if key is None:
        # Return failure message
        pass
    else:
        # Return game state (possibly with 'posted=True')
        pass
