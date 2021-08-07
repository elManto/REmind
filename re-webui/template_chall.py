import json
from os.path import *
from os import listdir
import time

from .db import *

ID = 0

get_timestamp = lambda: int(round(time.time() * 1000))


def getFiles(my_path):
    return [f for f in listdir(my_path) if isfile(join(my_path, f))]


def checkSolves(db, user_id, experiment_mode):
    solves = fetch_solutions(db, (user_id,))
    solved_challs = 0
    for row in solves:
        solved_challs += 1
    if experiment_mode == 1:
        return 3
    return solved_challs


def get_json_path(filename, json_path):
    json_file = join(json_path, filename)
    return join(dirname(realpath(__file__)), json_file)


def log_function(db, challenge_num, function_name, uid):
    timestamp = get_timestamp()
    event = json.dumps({'timestamp': timestamp, 'event':'function_visit', 'element':'', 'fcn_name':function_name})
    store_events(db, (uid, challenge_num, function_name, event))


def index_template(session, challenge_num, experiment_mode, obfuscation, request, json_path, g):
    s = checkSolves(get_db(), session['user_id'], experiment_mode)

    key = 'obfuscation_' + str(challenge_num)
    session[key] = obfuscation

    session['challenge_num'] = challenge_num
    function_map = dict()
    function_name = (request.args.get('function'))
    if(request.args.get('addr') is None):
        session['addr'] = '0'
    else:
        session['addr'] = request.args.get('addr')

    db = get_db()
    fetched_users = fetch_user_by_id(db, (session['user_id'],)
    )
    if len(fetched_users) > 0:
        g.user = fetched_users[0]
    else:
        return False
    functions = open(get_json_path('functions.json', json_path))
    for f in functions:
        function_map[f[:-1]] = f[:-1]

    func_rename = fetch_functions_by_id(db, (session['user_id'], challenge_num))
    real_old_name = ''
    for f in sorted(func_rename):
        old_name = f[2]
        new_name = f[3]
        if old_name in function_map:
            # default case when renaming a function just once
            function_map[old_name] = new_name       # old name : new name
        if old_name in function_map.values():
            # this is to handle when we have multiple rename of the same functions
            real_old_name = list(function_map.keys())[list(function_map.values()).index(old_name)]
            function_map[real_old_name] = new_name

        
        if new_name == function_name:
            function_name = real_old_name if real_old_name != '' else old_name

    log_function(db, challenge_num, function_name, session['user_id'])
    session['functions'] = function_map
    session['function_name'] = function_name
    close_db()
    return True


def strings_template(session, json_path, g, experiment_mode, challenge_num):
    s = checkSolves(get_db(), session['user_id'], experiment_mode)
    if s < 2:
        return False
    functions = open(get_json_path('functions.json', json_path))
    function_map = {f[:-1]:f[:-1] for f in functions}
    db = get_db()
    func_rename = fetch_functions_by_id(db, (session['user_id'], challenge_num))
    for f in sorted(func_rename):
        old_name = f[2]
        new_name = f[3]
        if old_name in function_map:
            # default case when renaming a function just once
            function_map[old_name] = new_name       # old name : new name
        if old_name in function_map.values():
            # this is to handle when we have multiple rename of the same functions
            real_old_name = list(function_map.keys())[list(function_map.values()).index(old_name)]
            function_map[real_old_name] = new_name

    session['functions'] = function_map
    strings = open(get_json_path('strings.json', json_path))
    string_dict = json.loads(strings.readlines()[0])
    g.user = fetch_user_by_id(db, (session['user_id'],))
    session['strings'] = string_dict
    close_db()
    return True


def confirm_solution_template(session, experiment_mode):
    s = checkSolves(get_db(), session['user_id'], experiment_mode)
    close_db()
    if s < 2:
        return False
    return True


def check_solution_template(request, session, challenge_num, solution):
    db = get_db()
    ans = request.form['solution']
    if ans == solution:
        store_solution(db, (session.get('user_id'), challenge_num, ans))
        session['status_solutions'][challenge_num] = 1
        close_db()
        return True
    else:
        close_db()
        return False

        
def callgraph_template(session, json_path, g, experiment_mode, challenge_num):
    db = get_db()
    s = checkSolves(db, session['user_id'], experiment_mode)
    if s < 2:
        close_db()
        return False

    functions = open(get_json_path('functions.json', json_path))
    function_map = {f[:-1]:f[:-1] for f in functions}
    func_rename = fetch_functions_by_id(db, (session['user_id'], challenge_num))

    for f in sorted(func_rename):
        old_name = f[2]
        new_name = f[3]
        if old_name in function_map:
            # default case when renaming a function just once
            function_map[old_name] = new_name       # old name : new name
        if old_name in function_map.values():
            # this is to handle when we have multiple rename of the same functions
            real_old_name = list(function_map.keys())[list(function_map.values()).index(old_name)]
            function_map[real_old_name] = new_name

    session['functions'] = function_map
    g.user = fetch_user_by_id(db, (session['user_id'],))
    close_db()
    return True


def get_call_graph_template(request, json_path):
    if(request.method == 'POST'):
        func_required = request.form['name']
        if(func_required == 'callgraph'):
            f = open(get_json_path(func_required + '.json', json_path))
            out = f.read()
            return out
        return ""


def info_template(session, json_path, g, experiment_mode, challenge_num):
    s = checkSolves(get_db(), session['user_id'], experiment_mode)
    if s < 2:
        close_db()
        return False

    functions = open(get_json_path('functions.json', json_path))
    function_map = {f[:-1]:f[:-1] for f in functions}
    db = get_db()
    func_rename = fetch_functions_by_id(db, (session['user_id'], challenge_num))
    for f in sorted(func_rename):
        old_name = f[2]
        new_name = f[3]
        if old_name in function_map:
            # default case when renaming a function just once
            function_map[old_name] = new_name       # old name : new name
        if old_name in function_map.values():
            # this is to handle when we have multiple rename of the same functions
            real_old_name = list(function_map.keys())[list(function_map.values()).index(old_name)]
            function_map[real_old_name] = new_name

    session['functions'] = function_map
    info = open(get_json_path('info.json', json_path))
    info_dict = json.loads(info.readlines()[0])
    g.user = fetch_user_by_id(db, (session['user_id'],))
    session['info'] = info_dict
    close_db()
    return True


def store_notes_template(request):
    if(request.method == 'POST'):
        tmp_token = request.form['token']
        notes = request.form['notes']
        db = get_db()
        user = fetch_user_by_tmp_token(db, (tmp_token,))[0]
        if user is None:
            close_db()
            return False
        store_notes(db, (user[ID], challenge_num, notes))
        close_db()
        return True


def download_notes_template(request):
    if(request.method == 'POST'):
        tmp_token = request.form['token']
        db = get_db()
        user = fetch_user_by_tmp_token(db, (tmp_token,))[0]
        if user is None:
            return False
        note = fetch_notes(db, (user[ID], challenge_num))
        close_db()
        return note[3]


def get_CFG_template(request, json_path, challenge_num):
    if(request.method == 'POST'):
        tmp_token = request.form['token']
        db = get_db()
        users = fetch_user_by_tmp_token(db, (tmp_token,))
        try:
            user = users[0]
        except:
            close_db()
            return False        
        if user is None:
            close_db()
            return False

        absolutePath = dirname(realpath(__file__))
        func_required = request.form['name']
        files = getFiles(join(absolutePath, json_path))
        if(func_required + '.json' in files):
            f = open(get_json_path(func_required + '.json', json_path))
            out = f.read()
            func_rename = fetch_functions_by_id(db, (user[ID], challenge_num))
            out_dict = json.loads(out)
            strings = open(get_json_path('strings.json', json_path))
            string_dict = json.loads(strings.readlines()[0])
            for key in string_dict:
                if(string_dict[key][0]['xref'][0] == func_required):
                    disasm = json.dumps(out_dict[func_required + "_bbs"])
                    local_addr = string_dict[key][2]['addr'][0]
                    start = disasm.index(local_addr + ":")
                    end = start
                    while(disasm[end] != '\\'):
                        end += 1
                    new_disasm = disasm[:start] + local_addr + ": " + string_dict[key][3]['opcode'][0] + disasm[end:]
                    out_dict[func_required + "_bbs"] = json.loads(new_disasm)

            # replacing function renaming
            for foo in func_rename:
                if json.dumps(out_dict[func_required + "_bbs"]).__contains__(foo[2]):
                    replaced_str = json.dumps(out_dict[func_required + "_bbs"]).replace(foo[2], foo[3])
                    out_dict[func_required + "_bbs"] = json.loads(replaced_str)
            close_db()

            res = json.dumps(out_dict)
            return res
        return ""


def get_xrefs_from_template(request, json_path, challenge_num):
    if(request.method == 'POST'):
        func_required = request.form['name']
        tmp_token = request.form['token']
        db = get_db()
        try:
            user = fetch_user_by_tmp_token(db, (tmp_token,))[0]
        except:
            close_db()
            return "Unauthenticated data"
        if user is None:
            close_db()
            return "Unauthenticated data"

        xref_file = open(get_json_path('xrefs_from.json', json_path))
        xref_dict = json.loads(xref_file.readlines()[0])

        if not func_required in xref_dict:
            close_db()
            return ""

        xrefs2addr = {foo.split("@")[0]:foo.split("@")[1] for foo in xref_dict[func_required]}

        # list_of_xrefs = [foo.split("@")[0] for foo in xref_dict[func_required]]
        func_rename = fetch_functions_by_id(db, (user[ID], challenge_num))
        res = dict()
        for foo in func_rename:
            old_name = foo[2]
            new_name = foo[3]
            if old_name in xrefs2addr.keys():
                res[old_name + "&&addr=" + xrefs2addr[old_name]] = new_name
            if old_name in res.values():
                # this is to handle when we have multiple rename of the same functions
                real_old_name = list(res.keys())[list(res.values()).index(old_name)]
                res[real_old_name] = new_name

        for foo in xrefs2addr:
            k = foo + "&&addr=" + xrefs2addr[foo]
            if not k in res.keys():
                res[foo + "&&addr=" + xrefs2addr[foo]] = foo
        close_db()
        return json.dumps(res)



def get_xrefs_to_template(request, json_path, challenge_num):
    if (request.method == 'POST'):
        func_required = request.form['name']
        tmp_token = request.form['token']
        db = get_db()
        users = fetch_user_by_tmp_token(db, (tmp_token,))
        try:
            user = users[0]
        except:
            close_db()
            return False
        if user is None:
            close_db()
            return False

        xref_file = open(get_json_path('xrefs_to.json', json_path))
        xref_dict = json.loads(xref_file.readlines()[0])
        if not func_required in xref_dict:
            close_db()
            return ""
        func_rename = fetch_functions_by_id(db, (user[ID], challenge_num))
        res = dict()
        for foo in func_rename:
            old_name = foo[2]
            new_name = foo[3]
            if old_name in xref_dict[func_required]:
                res[old_name] = new_name
            if old_name in res.values():
                # this is to handle when we have multiple rename of the same functions
                real_old_name = list(res.keys())[list(res.values()).index(old_name)]
                res[real_old_name] = new_name

        for foo in xref_dict[func_required]:
            if not foo in res.keys():
                res[foo] = foo
        close_db()
        return json.dumps(res)


def get_js_data_template(jsdata, challenge_num):
    data = jsdata.split(";")
    if (len(data) != 2):
        return "Wrong request"
    db = get_db()
    user = fetch_user_by_tmp_token(db, (data[0],))[0]
    if user is None:
        close_db()
        return "Unauthenticated data"
    d = json.loads(data[1])

    if(d['event'] == 'func_rename'):
        store_new_function_name(db, (user[ID], d["element"], d["value"], challenge_num))

    store_events(db, (user[ID], challenge_num, d["fcn_name"], data[1]))
    close_db()
    return "Ok"


def get_events_from_db_template(request, challenge_num):
    id = request.args.get('id')
    fcn_name = request.args.get('fcn_name')
    # query to db with id=='id' to retrieve the events
    db = get_db()
    user = fetch_user_by_tmp_token(db, (id,))[0]
    if user is None:
        close_db()
        return False

    events = fetch_events(db, (user[ID], challenge_num, fcn_name))
    response = []
    for e in events:
        d = json.loads(e[0])
        if d['event'] == 'comment' or d['event'] == 'rename' or d['event'] == 'func_rename':
            response.append(d)
    close_db()
    return json.dumps(response)


def load_logged_in_user_template(session, g):
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = fetch_user_by_id(get_db(), (user_id,))[0]
        close_db()

