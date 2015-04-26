from user import User
import sqlite3
from flask import Flask, request, flash, abort
from flask import current_app as app
from flask_bootstrap import Bootstrap
from flask.ext.appconfig import AppConfig
from flask.ext.login import LoginManager, login_user, logout_user

# Constants
CONFIG_FILE = 'config.py'
INSERT_QUERY = "INSERT INTO users ('username', 'password', 'email', 'display') VALUES(?, ?, ?, ?)"

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
    user_data = {
        'display'  : request.form['display'],
        'username' : request.form['username'],
        'password' : request.form['password'],
        'confirm'  : request.form['confirm'],
        'email'    : request.form['email']
    }

    user = User.get(user_data['username'])
    print(user)

    if user_data['password'] != user_data['confirm']:
        # Passwords in the form do not match
        return 'Passwords do not match'
    elif user and user.check_password(user_data['password']):
        login_user(user)
        return None
    elif user:
        # Username already taken
        return 'Username already in use'
    else:
        add_user_to_db(user_data)

        user = User.get(user_data['username'])
        login_user(user)

        user.send_confirmation_email()
        # No error
        return None

def do_activate(payload):
    s = URLSafeSerializer(app.config['SECRET_KEY'])
    try:
        username = s.loads(payload)
    except BadSignature:
        abort(404)

    user = User.get(username)
    if not user or user.is_active():
        abort(404)
    user.set_active()
    flash('Account activated')

def add_user_to_db(user_data):
    # First salt and hash the password
    pw_hash = User.get_pw_hash(user_data['password'])

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    data = (user_data['username'], pw_hash, user_data['email'], user_data['display'], )
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
