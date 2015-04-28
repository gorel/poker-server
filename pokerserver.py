#!/usr/bin/python

"""
    Poker Server
    ============
    This is a simple poker server written in Flask that will be used to
    play simple poker games like Texas Hold'Em or Blackjack with easy
    endpoints for bots to connect to.  I hope to use it with ACM to allow
    others to adapt it to create AI competitions.

    Author: Logan Gore

"""

# Imports
import os
from utils import *
from user import User
from flask import request, redirect, url_for, render_template, flash
from flask.ext.login import login_required, current_user

# The app
app = create_app(__name__)
login_manager = create_login_manager(app)

# Login manager handlers
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Error handlers
@app.errorhandler(404)
def show_404_error(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def show_403_error(e):
    return render_template('403.html'), 403

# Routing information
@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    info = request.args.get('info')
    error = request.args.get('error')
    return render_template('index.html', info=info, error=error)

@app.route('/api')
def api():
    error = errors.get(request.args.get('error'))
    return render_template('api.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    messages = do_login()
    return redirect(request.args.get('next') or url_for('index', **messages))

@app.route('/logout')
@login_required
def logout():
    messages = do_logout()
    return redirect(request.args.get('next') or url_for('index', **messages))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        error = errors.get(request.args.get('error'))
        return render_template('register.html', error=error)
    else:
        messages = do_register()
        return redirect(request.args.get('next') or url_for('index', **messages))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        current_user.generate_api_key()
    return render_template('account.html')

@app.route('/account/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'GET':
        error = errors.get(request.args.get('error'))
        return render_template('settings.html', error=error)
    else:
        messages = do_account_update()
        return redirect(request.args.get('next') or url_for('account', **messages))

@app.route('/account/activate')
@app.route('/account/activate/<payload>')
def activate(payload=None):
    if payload is None:
        # TODO: Finish setting up email confirmation
        #current_user.send_confirmation_email()
        return redirect(request.args.get('next') or url_for('account'))
    else:
        do_activate(payload)
        return redirect(url_for('index'))

@app.route('/account/forgot', methods=['GET', 'POST'])
@app.route('/account/forgot/<payload>', methods=['GET', 'POST'])
def forgot(payload=None):
    if payload is None:
        if request.method == 'POST':
            messages = send_password_reset()
            return redirect(request.args.get('next') or url_for('index' **messages))
        else:
            error = errors.get(request.args.get('error'))
            return render_template('forgot.html', error=error)
    else:
        if request.method == 'POST':
            messages = do_password_reset(payload)
            return redirect(request.args.get('next') or url_for('index', **messages))
        else:
            error = errors.get(request.args.get('error'))
            return render_template('reset.html', error=error)

@app.route('/account/delete/<name>')
@login_required
def delete(name):
    if not current_user.is_administrator():
        abort(403)

    messages = do_delete(name)
    return redirect(request.args.get('next') or url_for('admin', **messages))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_administrator():
        abort(403)

    messages = {}
    if request.method == 'POST':
        messages = do_admin_actions()
    users = User.getall()
    return render_template('admin.html', users=users, **messages)

@app.route('/tables')
def tables():
    error = errors.get(request.args.get('error'))
    return render_template('tables.html', error=error)

@app.route('/scoreboard')
def scoreboard():
    error = errors.get(request.args.get('error'))
    return render_template('scoreboard.html', error=error)

@app.route('/play', methods=['GET', 'POST'])
def play():
    if request.method == 'GET':
        return render_json()
    else:
        posted = post_action()
        return render_json(posted=posted)

# Start the server
if __name__ == '__main__':
    # TODO: Start a poker server here?
    app.run()
