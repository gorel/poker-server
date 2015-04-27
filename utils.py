from user import User
import sqlite3
from flask import Flask, request, flash, abort
from flask import current_app as app
from flask_bootstrap import Bootstrap
from flask.ext.appconfig import AppConfig
from flask.ext.login import LoginManager, login_user, logout_user, current_user

# Constants
CONFIG_FILE = 'config.py'
CHECK_DISPLAY_QUERY = "SELECT * FROM users WHERE display=?"
INSERT_QUERY = "INSERT INTO users ('username', 'password', 'email', 'display') VALUES(?, ?, ?, ?)"
UPDATE_QUERY = "UPDATE users SET display=?, email=? WHERE id=?"
UPDATE_PW_QUERY = "UPDATE users SET password=? WHERE id=?"
DISPLAY_COLUMN = 4

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

def display_taken(display):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    data = (display, )
    c.execute(CHECK_DISPLAY_QUERY, data)
    result = c.fetchone()
    conn.close()
    return result and result[DISPLAY_COLUMN] != current_user.get_display()

def do_login():
    username = request.form['username']
    password = request.form['password']
    remember = request.args.get('remember')

    user = User.get(username)
    if user and user.check_password(password):
        login_user(user, remember=remember, force=True)
        return None
    elif user:
        return "inc_password"
    else:
        return "unknown_user"

def do_register():
    user_data = {
        'display'  : request.form['display'],
        'username' : request.form['username'],
        'password' : request.form['password'],
        'confirm'  : request.form['confirm'],
        'email'    : request.form['email']
    }

    user = User.get(user_data['username'])

    if user_data['password'] != user_data['confirm']:
        # Passwords in the form do not match
        return "pass_match"
    elif display_taken(user_data['display']):
        return "display_in_use"
    elif user and user.check_password(user_data['password']):
        login_user(user, force=True)
        return None
    elif user:
        # Username already taken
        return "user_in_use"
    else:
        add_user_to_db(user_data)

        user = User.get(user_data['username'])
        login_user(user, force=True)

        # TODO: Finish email confirmation
        #user.send_confirmation_email()
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

def do_account_update():
    new_display = request.form.get('display')
    new_email = request.form.get('email')
    new_password = request.form.get('password')
    confirm = request.form.get('confirm')

    if display_taken(new_display):
        return "display_in_use"

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    if new_password:
        if new_password != confirm:
            return "pass_match"
        pw_hash = User.get_pw_hash(password)
        data = (pw_hash, current_user.get_user_id())
        c.execute(UPDATE_PW_QUERY, data)
    data = (new_display, new_email, current_user.get_user_id())
    c.execute(UPDATE_QUERY, data)
    conn.commit()
    conn.close()

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
