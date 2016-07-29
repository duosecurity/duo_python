import ConfigParser
import duo_web as duo
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

# config
DEBUG = True
SECRET_KEY = 'dev key'


# create flask application
app = Flask(__name__)
app.config.from_object(__name__)


# config parser
def grab_keys(filename='duo.conf'):
    config = ConfigParser.RawConfigParser()
    config.read(filename)

    akey = config.get('duo', 'akey')
    ikey = config.get('duo', 'ikey')
    skey = config.get('duo', 'skey')
    host = config.get('duo', 'host')
    return {'akey': akey, 'ikey': ikey, 'skey': skey, 'host': host}


# app-specific configs
def app_config(filename='app.conf'):
    config = ConfigParser.RawConfigParser()
    config.read(filename)
    return config.get('app', 'skey')


# Routing functions
@app.route('/')
def show_entries():
    return render_template('show_entries.html')


@app.route('/mfa', methods=['GET', 'POST'])
def mfa():
    result = grab_keys()
    sec = duo.sign_request(result['ikey'], result['skey'], result['akey'], session['user'])
    if request.method == 'GET':
        return render_template('duoframe.html', duohost=result['host'], sig_request=sec)
    if request.method == 'POST':
        user = duo.verify_response(result['ikey'], result['skey'], result['akey'], request.args.get('sig_response'))
        if user == session['user']:
            return render_template(url_for('mfa'), user=user)


@app.route('/success', methods=['POST'])
def success():
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == "":
            error = 'Invalid Username. Please type something.'
        else:
            session['logged_in'] = True
            session['user'] = request.form['username']
            flash('You were logged in')
            return redirect(url_for('mfa'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


# main body
if __name__ == '__main__':
    app.secret_key = app_config('app.conf')
    app.run()
