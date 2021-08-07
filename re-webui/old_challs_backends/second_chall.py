from flask import (
    Blueprint, g, render_template, request, session, redirect, url_for
)
import json
import configparser
import os
from os import listdir
from os.path import isfile, join

from auth import login_required
from db import get_db, read_query, write_query

bp = Blueprint('second_chall', __name__, url_prefix='/second_chall')
user = ()

config = configparser.ConfigParser()
config.read(os.path.dirname(os.path.realpath(__file__)) + '/config.ini')
n_challs = config['DEFAULT'].getint('challs')
challenge_num = 2

ID = 0

def getFiles(myPath):
    return [f for f in listdir(myPath) if isfile(join(myPath, f))]


def get_submitted_solutions(db, user_id):
    sols = dict()
    for i in range(1, n_challs):
        sols[i] = 0
    solves = read_query(db,
        'SELECT * FROM solutions WHERE user_id = ? GROUP BY challenge', (user_id,)
    )
    for s in solves:
        sols[s[2]] = 1
    return sols


@bp.route('/')
@login_required
def second_chall():

    solutions = get_submitted_solutions(get_db(), session['user_id'])
    solved = 0
    for s in solutions:
        if solutions[s] == 1:
            solved += 1
    if solved < 2:
        return render_template("cannot_access.html")
    return render_template("second_chall.html")


@bp.route('/questions', methods=('GET', 'POST'))
@login_required
def questions():
    s = get_submitted_solutions(get_db(), session['user_id'])
    if len(s) < 2:
        return render_template("cannot_access.html")
    if request.method == 'POST':

        js_ans = json.dumps(request.form)
        db = get_db()
        write_query(db,
            'INSERT INTO solutions (user_id, challenge, solution) values(?, ?, ?)',
            (session.get('user_id'), challenge_num, js_ans)
        )
        session['status_solutions']['1'] = 1
        return redirect(url_for('rev_webui.index'))

    return render_template("questions.html")


@bp.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = read_query(db,
            'SELECT * FROM user WHERE id = ?', (user_id,)
        )[0]
