from flask import (
    Blueprint, g, render_template, request, session
)
import json
import os
from os import listdir
from os.path import isfile, join
import configparser

from auth import login_required
from db import get_db, read_query, write_query

bp = Blueprint('sixth_chall', __name__, url_prefix='/sixth_chall')
user = ()

config = configparser.ConfigParser()
config.read(os.path.dirname(os.path.realpath(__file__)) + '/config.ini')
challenge_num = config['chall6'].getint('challenge_num')
solution = config['chall6']['solution']
n_challs = config['DEFAULT'].getint('challs')

ID = 0


def getFiles(myPath):
    return [f for f in listdir(myPath) if isfile(join(myPath, f))]


def check_solution(r):
    sol = solution.split(';')
    return r == sol[0] or r == sol[1]


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
def sixth_chall():
    solutions = get_submitted_solutions(get_db(), session['user_id'])
    session['status_solutions'] = solutions

    solved = 0
    for s in solutions:
        if solutions[s] == 1:
            solved += 1
    if solved < 2:
        return render_template("cannot_access.html")
    if session['status_solutions'][challenge_num] == 1:
        session['speed_solved_2'] = True
    return render_template("sixth_chall.html")


@bp.route('/getBlock', methods=['POST'])
def getBlock():
    if (request.method == 'POST'):
        tmp_token = request.form['token']

        db = get_db()
        user = read_query(db,
            'SELECT * FROM user WHERE tmp_token = ?', (tmp_token,)
        )[0]
        if user is None:
            return "Unauthenticated data"

        absolutePath = os.path.dirname(os.path.realpath(__file__))
        func_required = request.form['name']
        files = getFiles(absolutePath + '/sixth_json/')
        if (func_required + '.json' in files):
            f = open(absolutePath + '/sixth_json/' + func_required + '.json')
            out = f.read()

            out_dict = json.loads(out)

            return json.dumps(out_dict)
        return ""


@bp.route('/storeSolution', methods=['POST'])
def storeSolution():
    if(request.method == 'POST'):
        tmp_token = request.form['token']
        notes = request.form['notes']

        data = notes.split(";")
        res = data[0]

        db = get_db()
        user = read_query(db,
            'SELECT * FROM user WHERE tmp_token = ?', (tmp_token,)
        )[0]
        if user is None:
            return "Unauthenticated data"
        write_query(db,
            'INSERT INTO solutions (user_id, challenge, solution) VALUES (?, ?, ?)',
            (user[ID], challenge_num, notes)
        )
        if (not check_solution(res)):
            return "0"
        session['speed_solved_2'] = True
        session['status_solutions'][challenge_num] = 1
        return "1"


@bp.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = read_query(get_db(),
            'SELECT * FROM user WHERE id = ?', (user_id,)
        )[0]
