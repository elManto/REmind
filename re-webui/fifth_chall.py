from flask import (
    Blueprint, g, render_template, request, session, url_for
)
from werkzeug.utils import redirect
import json
import os
import configparser
from os import listdir
from os.path import isfile, join

from .config import get_chall_config

from .auth import login_required
from .db import *

from .template_chall import *

bp = Blueprint('fifth_chall', __name__, url_prefix='/fifth_chall', template_folder='templates/template_fifth/')
user = ()

CHALL_ID = 5
ID = 0

config = get_chall_config(CHALL_ID)
challenge_num = CHALL_ID 
obfuscation = config['obfuscation']
experiment_mode = int(config['experiment_mode'])
solution = config['solution']
json_path = './jsons/fifth_json/'


@bp.route('/')
@login_required
def fifth_chall():
    r = index_template(session, challenge_num, experiment_mode, obfuscation, request, json_path, g)
    if r:
        return render_template('fifth_chall.html')
    else:
        return render_template('cannot_access.html')


@bp.route('/strings')
@login_required
def strings():
    r = strings_template(session, json_path, g, experiment_mode, challenge_num)
    if r:
        return render_template('strings_5.html')
    else:
        return render_template('cannot_access.html')


@bp.route('/confirm_solution', methods=('GET', 'POST'))
@login_required
def confirm_solution():
    if request.method == 'GET':
        r = confirm_solution_template(session, experiment_mode)
        if r:
            return render_template("confirm_solution_5.html")
        else:
            return render_template("cannot_access.html")
    elif request.method == 'POST':
        r = check_solution_template(request, session, challenge_num, solution)
        if r:
            return redirect(url_for('rev_webui.congrats'))
        else:
            return redirect(url_for('rev_webui.wrong'))
    else:
        return render_template("confirm_solution_5.html")
        

@bp.route('/callgraph')
@login_required
def callgraph():
    r = callgraph_template(session, json_path, g, experiment_mode) 
    if r:
        return render_template("callgraph_5.html")
    else:
        return render_template("cannot_access.html")


@bp.route('/getCallGraph', methods=['POST'])
def getCallGraph():
    r = get_call_graph_template(request, json_path)
    return r


@bp.route('/info')
@login_required
def info():
    r = info_template(session, json_path, g, experiment_mode, challenge_num)
    if r:
        return render_template("info_5.html")
    else:
        return render_template("cannot_access.html")


@bp.route('/storeNotes', methods=['POST'])
def storeNotes():
    r = store_notes_template(request)
    if r:
        return "ok"
    else:
        return "Unauthenticated data"


@bp.route('/downloadNotes', methods=['POST'])
def downloadNotes():
    r = download_notes_template(request)
    if r:
        return r
    return "Unauthenticated data"


@bp.route('/getCFG', methods=['POST'])
def getCFG():
    r = get_CFG_template(request, json_path, challenge_num)
    if r:
        return r
    return "Unauthenticated data"


@bp.route('/get_xrefs_from', methods=['POST'])
def get_xrefs_from():
    r = get_xrefs_from_template(request, json_path, challenge_num)
    if r:
        return r
    return "Unauthenticated data"


@bp.route('/get_xrefs_to', methods=['POST'])
def get_xrefs_to():
    r = get_xrefs_to_template(request, json_path, challenge_num)
    if r:
        return r
    return "Unauthenticated data"


# endpoint for sending json data
@bp.route('/getmethod/<jsdata>')
def get_js_data(jsdata):
    return get_js_data_template(jsdata, challenge_num) 


@bp.route('/getevents/')
def get_events_from_db():
    r = get_events_from_db_template(request, challenge_num) 
    if r:
        return r
    return "Unauthenticated data"


@bp.before_request
def load_logged_in_user():
    load_logged_in_user_template(session, g) 
