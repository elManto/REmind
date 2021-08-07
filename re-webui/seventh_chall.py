from flask import (
    Blueprint, g, render_template, request, session
)
import json
import os
import configparser
from os import listdir
from os.path import isfile, join

from .config import get_chall_config
from .db import *
from .auth import login_required
from .template_chall import *

bp = Blueprint('seventh_chall', __name__, url_prefix='/seventh_chall', template_folder='templates/template_seventh/')
user = ()

CHALL_ID = 7
ID = 0

config = get_chall_config(CHALL_ID)
challenge_num = CHALL_ID 
obfuscation = config['obfuscation']
experiment_mode = int(config['experiment_mode'])
json_path = './jsons/seventh_json/'


@bp.route('/')
@login_required
def seventh_chall():
    r = index_template(session, challenge_num, experiment_mode, obfuscation, request, json_path, g)
    if r:
        return render_template('seventh_chall.html')
    else:
        return render_template('cannot_access.html')


@bp.route('/strings')
@login_required
def strings():
    r = strings_template(session, json_path, g, experiment_mode, challenge_num)
    r = False
    if r:
        return render_template('strings_7.html')
    else:
        return render_template('cannot_access.html')


@bp.route('/confirm_solution', methods=('GET', 'POST'))
@login_required
def confirm_solution():
    r = confirm_solution_template(session, experiment_mode)
    if r:
        return render_template("confirm_solution_7.html")
    else:
        return render_template("cannot_access.html")
    

@bp.route('/callgraph')
@login_required
def callgraph():
    r = callgraph_template(session, json_path, g, experiment_mode, challenge_num) 
    if r:
        return render_template("callgraph_7.html")
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
        return render_template("info_7.html")
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
