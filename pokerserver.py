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

# Routing information
@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/api')
def api():
    return render_template('api.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = do_login()
    if error:
        # TODO: Add error output and try again
        pass
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        do_register()
        return redirect(request.args.get('next') or url_for('index'))

@app.route('/account')
@login_required
def account():
    if current_user.is_authenticated():
        return render_template('account.html')
    else:
        return redirect(request.args.get('next') or url_for('login'))

@app.route('/account/activate/<payload>')
def activate(payload):
    do_activate(payload)
    return redirect(url_for('index'))


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        do_admin_actions()
    return render_template('admin.html')

@app.route('/tables')
def tables():
    return render_template('tables.html')

@app.route('/scoreboard')
def scoreboard():
    return render_template('scoreboard.html')

@app.route('/play', methods=['GET', 'POST'])
def play():
    if request.method == 'GET':
        return render_json()
    else:
        post_action()
        return render_json(posted=True)

# Start the server
if __name__ == '__main__':
    # TODO: Start a poker server here?
    app.run()
