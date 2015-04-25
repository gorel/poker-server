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
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, send_from_directory
from flask_bootstrap import Bootstrap
from flask.ext.appconfig import AppConfig

# App creation function
def create_app(configfile=None):
    app = Flask(__name__)
    Bootstrap(app)
    AppConfig(app, configfile)
    return app

# Constants
CONFIG_FILE = 'config.py'
app = create_app(CONFIG_FILE)

# Error handlers
@app.errorhandler(404)
def show_404_error(e):
    return render_template('404.html'), 404

# Routing information
@app.route('/')
@app.route('/index')
@app.route('/index.html')
def show_homepage():
    if 'username' in session:
        return render_template('index.html', name=session['username'])
    else:
        return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def show_login():
    if request.method == 'POST':
        # Login user
        pass
    else:
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def show_register():
    if request.method == 'POST':
        # Register user
        pass
    else:
        return render_template('register.html')

@app.route('/account')
def show_account_page():
    if 'username' in session:
        return render_template('account.html')
    else:
        redirect(url_for('/login'))

@app.route('/admin', methods=['GET', 'POST'])
def show_admin_page():
    if request.method == 'POST':
        # Do admin actions
        pass
    else:
        return render_template('admin.html')

@app.route('/tables')
def show_tables():
    return render_template('tables.html')

@app.route('/scoreboard')
def show_scoreboard():
    return render_template('scoreboard.html')

# Start the server
if __name__ == '__main__':
    # TODO: Start a poker server here?
    app.run()
