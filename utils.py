from user import User
from errors import *
from dbhelper import *
from gamehelper import *
import sqlite3
import subprocess
from itsdangerous import URLSafeSerializer
from flask import Flask, request, flash, abort, jsonify
from flask import current_app as app
from flask_bootstrap import Bootstrap
from flask.ext.appconfig import AppConfig
from flask.ext.login import LoginManager, login_user, logout_user, current_user

# Constants
CONFIG_FILE = 'config.py'
CHECK_DISPLAY_QUERY = "SELECT * FROM users WHERE display=?"
INSERT_QUERY = "INSERT INTO users ('username', 'password', 'email', 'display') VALUES(?, ?, ?, ?)"
UPDATE_QUERY = "UPDATE users SET display=?, email=? WHERE id=?"
UPDATE_PW_QUERY = "UPDATE users SET password=?, pw_reset=NULL WHERE id=?"
UPDATE_ACTIVE_QUERY = "UPDATE users SET active=? WHERE id=?"
UPDATE_ADMIN_QUERY = "UPDATE users SET admin=? WHERE id=?"
DELETE_QUERY = "DELETE FROM users WHERE display=?"

DAEMON_RUNNING_MESSAGE = "Daemon is running"
CHECK_DAEMON_COMMAND = ["./pokerdaemon.py", "status"]
START_DAEMON_COMMAND = ["./pokerdaemon.py", "start"]
STOP_DAEMON_COMMAND  = ["./pokerdaemon.py", "stop"]

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
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    data = (display, )
    c.execute(CHECK_DISPLAY_QUERY, data)
    result = c.fetchone()
    conn.close()
    if current_user.is_authenticated():
        return result and result[USER_DISPLAY_COLUMN] != current_user.get_display()
    else:
        return result

def do_login():
    messages = {}
    username = request.form.get('username')
    password = request.form.get('password')
    remember = request.args.get('remember')

    user = User.get(username)
    if user and user.check_password(password):
        login_user(user, remember=remember, force=True)
    elif user:
        messages['error'] = errors.get("inc_password")
    else:
        messages['error'] = errors.get("unknown_user")
    return messages

def do_logout():
    messages = {}
    logout_user()
    messages['info'] = infos.get("logout_success")
    return messages

def do_register():
    messages = {}
    user_data = {
        'display'  : request.form.get('display'),
        'username' : request.form.get('username'),
        'password' : request.form.get('password'),
        'confirm'  : request.form.get('confirm'),
        'email'    : request.form.get('email')
    }

    user = User.get(user_data['username'])

    if user_data['password'] != user_data['confirm']:
        messages['error'] = errors.get("pass_match")
    elif display_taken(user_data['display']):
        messages['error'] = errors.get("display_in_use")
    elif user and user.check_password(user_data['password']):
        login_user(user, force=True)
    elif user:
        messages['error'] = errors.get("user_in_use")
    else:
        add_user_to_db(user_data)

        user = User.get(user_data['username'])
        login_user(user, force=True)

        user.send_activation_email()
    return messages

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
    messages = {}
    new_display = request.form.get('display')
    new_email = request.form.get('email')
    new_password = request.form.get('password')
    confirm = request.form.get('confirm')

    if display_taken(new_display):
        messages['error'] = errors.get("display_in_use")
    else:
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        if new_password:
            if new_password != confirm:
                messages['error'] = errors.get("pass_match")
            else:
                pw_hash = User.get_pw_hash(password)
                data = (pw_hash, current_user.get_user_id())
                c.execute(UPDATE_PW_QUERY, data)
        data = (new_display, new_email, current_user.get_user_id())
        c.execute(UPDATE_QUERY, data)
        conn.commit()
        conn.close()
    return messages

def send_password_reset():
    messages = {}
    email = request.form.get('email')

    user = User.get_by_email(email)
    if user is None:
        messages['error'] = errors.get("unknown_user")
    else:
        user.send_pw_reset_email()
        messages['info'] = infos.get("pw_reset_email")
    return messages

def do_password_reset(payload):
    messages = {}
    new_pass = request.form.get('password')
    confirm = request.form.get('confirm')
    user = User.get_by_pw_reset_key(payload)

    if new_pass != confirm:
        messages['error'] = errors.get("pass_match")
    elif user is None:
        messages['error'] = errors.get("invalid_reset")
    else:
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()

        data = (new_pass, user.get_user_id(), )
        c.execute(UPDATE_PW_QUERY, data)
        conn.commit()
        conn.close()
        login_user(user, force=True)
        messages['info'] = infos.get("reset_success")
    return messages

def add_user_to_db(user_data):
    # First salt and hash the password
    pw_hash = User.get_pw_hash(user_data['password'])

    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    data = (user_data['username'], pw_hash, user_data['email'], user_data['display'], )
    c.execute(INSERT_QUERY, data)
    conn.commit()
    conn.close()

def do_delete(name):
    messages = {}
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()

    data = (name, )
    c.execute(DELETE_QUERY, data)
    conn.commit()
    conn.close()

    messages['info'] = infos.get("delete_success")
    return messages

def do_admin_actions():
    messages = {}
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()

    # Admin is starting or stopping the poker daemon
    if "start" in request.form:
        messages.update(start_daemon())
    elif "stop" in request.form:
        messages.update(stop_daemon())
    else:
        for field in request.form:
            value = int(request.form.get(field))
            # Ignore the hidden attribute if the checkbox is active
            if ".hidden" in field:
                field = field.split(".hidden")[0]
                if field in request.form:
                    continue


            if "active" in field:
                user = int(field.split("active")[1])
                data = (value, user, )
                c.execute(UPDATE_ACTIVE_QUERY, data)
            elif "admin" in field:
                user_id = int(field.split("admin")[1])
                # Don't allow the user to delete their own administrator access
                if user_id != current_user.get_user_id():
                    data = (value, user_id, )
                    c.execute(UPDATE_ADMIN_QUERY, data)
        conn.commit()
        conn.close()
        messages['info'] = infos.get("field_success")
    return messages

def post_action(player, action, amount=0):
    if action is None:
        return False
    elif action is "bet" and amount is None:
        return False
    elif action not in VALID_ACTIONS:
        return False
    else:
        player.post_action(action, amount)
        return True


def render_json(player, posted=False):
    game_state = load_game_state(player, posted)
    return jsonify(**game_state)

def load_game_state(player, posted):
    table_state = TableState.get(player)
    opponents = Player.get_opponents(player)
    bet_so_far = player.get_initial_stack() - player.get_stack()
    call_amount = table_state.get_current_bet - bet_so_far

    game_state = {}
    game_state['round_id'] = table_state.get_round_id()
    game_state['initial_stack'] = player.get_initial_stack()
    game_state['stack'] = player.get_stack()
    game_state['current_bet'] = table_state.get_current_bet()
    game_state['call_amount'] = call_amount
    game_state['current_pot'] = table_state.get_current_pot()
    game_state['phase'] = table_state.get_phase()
    game_state['my_turn'] = player.get_my_turn()
    game_state['hand'] = player.get_hand()
    game_state['community'] = table_state.get_community_cards()
    game_state['opponents'] = opponents

    if posted:
        game_state['posted'] = True

    return game_state

def get_daemon_status():
    out = subprocess.check_output(CHECK_DAEMON_COMMAND).strip()
    return out == DAEMON_RUNNING_MESSAGE

def start_daemon():
    ret = subprocess.call(START_DAEMON_COMMAND)
    if ret == 0:
        return {'info': infos.get("daemon_start")}
    else:
        return {'error': errors.get("daemon_start")}

def stop_daemon():
    ret = subprocess.call(STOP_DAEMON_COMMAND)
    if ret == 0:
        return {'info': infos.get("daemon_stop")}
    else:
        return {'error': errors.get("daemon_stop")}
