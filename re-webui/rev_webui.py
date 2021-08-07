from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, send_file
)
import os
import time
import json

from .db import get_db, write_query, read_query
from .config import get_general_config
from .auth import login_required

bp = Blueprint('rev_webui', __name__, template_folder='templates/general/')
user = ()

conf = get_general_config()
n_challs = conf['challs']
experiment_mode = conf['experiment_mode']

SOLVES = 4

get_timestamp = lambda: int(round(time.time() * 1000))

def get_submitted_solutions(db, user_id):
    sols = dict()
    for i in range(1, n_challs):
        sols[i] = 0
    solves = read_query(db,
        'SELECT * FROM solutions WHERE user_id = %s GROUP BY challenge', (user_id,)
    )
    for s in solves:
        sols[s[2]] = 1
    return sols


@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    ex_func = request.args.get('func')
    db = get_db()
    if(ex_func is not None):
        ex_addr = request.args.get('addr')
    g.user = read_query(db,
        'SELECT * FROM user WHERE id = %s', (session['user_id'],)
    )[0] 
    user_id = session.get('user_id')
    session['solves'] = g.user[SOLVES] 
    if request.method == 'POST':
        solution = request.form['solution']
        solution_json = json.dumps({'timestamp' : get_timestamp(), 'solution' : solution})
        user_id = session.get('user_id')
        if 'challenge_num' in session:
            challenge_num = session.get('challenge_num')
        else:
            challenge_num = 1
        write_query(db,
            'INSERT INTO solutions (user_id, challenge, solution) VALUES (%s, %s, %s)', 
            (user_id, challenge_num, solution_json)
        )
   
    solves = read_query(db,
        'SELECT * FROM solutions WHERE user_id = %s group by challenge', (user_id,)
    )
    session['solves'] = len(solves)
    session['status_solutions'] = get_submitted_solutions(db, user_id)
    # check the number of solved challs to access the further challs
    if experiment_mode == 1:
        session['experiment_mode'] = 1
        session['solves'] = 3
    else:
        session['experiment_mode'] = 0
    return render_template("challs.html")


@bp.route('/congrats')
@login_required
def congrats():
    return render_template("congrats.html")



@bp.route('/wrong')
@login_required
def wrong():
    return render_template("wrong.html")

'''
@bp.route('/download')
@login_required
def download():
    if(session['solves'] < 2):
        return render_template("cannot_access.html")
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), './../test/lvl_3_4.tgz')
    return send_file(path, as_attachment=True)
'''

@bp.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        u = read_query(get_db(),
            'SELECT * FROM user WHERE id = %s', (user_id,)
        )
        if u:
            g.user = u[0]
        else:
            g.user = None


