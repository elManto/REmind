import functools
import os
import binascii

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from .config import get_general_config
from .db import get_db, register_user, fetch_solutions, fetch_all_users, update_tmp_token, fetch_user_by_id

bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates/auth/')

conf = get_general_config()
experiment_mode = conf['experiment_mode']

ID = 0
TOKEN = 2

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        level = request.form['level']
        first_name = ''
        last_name = ''
        if experiment_mode == 0:
            first_name = request.form['first']
            last_name = request.form['last']
        ctf_freq = 0
        db = get_db()
        error = None
        token = binascii.hexlify(os.urandom(5)).decode('utf-8')
        #hashed_token = generate_password_hash(token)
        hashed_token = token
        val = (level, hashed_token, '', 0, first_name, last_name, '')
        register_user(db, val)
        session['just_logged'] = 1
        session['token'] = token
        return redirect(url_for('auth.login'))

        flash(error)
    session['experiment_mode'] = experiment_mode
    return render_template('register.html')


def get_submitted_solutions(db, user_id):
    sols = dict()
    for i in range(1, 8):
        sols[i] = 0
    val = (user_id,)
    solves = fetch_solutions(db, val)
    for s in solves:
        sols[s[2]] = 1
    return sols


def my_check_password(db_token, candidate_token):
    return db_token == candidate_token or check_password_hash(db_token, candidate_token)


@bp.route('/login', methods=('GET', 'POST'))
def login():

    if request.method == 'POST':
        token = request.form['token']
        db = get_db()
        error = None
        users = fetch_all_users(db)
        user = dict()
        for u in users:
            if(my_check_password(u[TOKEN], token)):
                user = u
                break

        if not user:
            error = 'Incorrect password'

        session.clear()
        if error is None:

            session['user_id'] = user[ID]
            session['status_solutions'] = get_submitted_solutions(db, user[ID])
            tmp_token = binascii.hexlify(os.urandom(10)).decode('utf-8')
            val = (tmp_token, user[ID])
            update_tmp_token(db, val)
            session['tmp_token'] = tmp_token

            return redirect(url_for('index'))

        flash(error)
    return render_template('login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        val = (user_id,)
        g.user = fetch_user_by_id(get_db(), val)


@bp.route('/logout')
def logout():
    id = session.get('user_id')
    db = get_db()
    val = ('', id)
    update_tmp_token(db, val)
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
