from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, send_file
    )
from flask_table import Table, Col
import configparser
import os

from .auth import login_required
from .db import get_db, write_query, read_query

bp = Blueprint('admin', __name__, url_prefix='/admin')
user = ()


config = configparser.ConfigParser()
config.read(os.path.dirname(os.path.realpath(__file__)) + '/config.ini')
n_challs = config['DEFAULT'].getint('challs')
admin_list = [int(admin_id) for admin_id in config['DEFAULT']['admin'].split(';') if admin_id != '']

ID = 0
TOKEN = 2
SOLVES = 4
FIRST_NAME = 5
LAST_NAME = 6


class ItemTable(Table):
    first_name = Col('First Name')
    last_name = Col('Second Name')
    chall_1 = Col('chall_1')
    chall_2 = Col('chall_2')
    test_1 = Col('test_1')
    test_2 = Col('test_2')


class Item(object):
    def __init__(self, first_name, last_name, chall_1, chall_2, test_1, test_2):
        self.first_name = first_name
        self.last_name = last_name
        self.chall_1 = chall_1
        self.chall_2 = chall_2
        self.test_1 = test_1
        self.test_2 = test_2


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


def get_itemized_users(db):
    users = read_query(db,
            'SELECT * FROM user', None
        )
    items = []
    for user in users:
        user_id = user[ID]
        if not is_admin(user_id):
            token = user[TOKEN]
            first_name = user[FIRST_NAME]
            last_name = user[LAST_NAME]
            solves = get_submitted_solutions(db, user_id)
            chall_1 = solves[4]
            chall_2 = solves[5]     # For this crazy mapping check the config.ini (the reason is that challs
            test_1 = solves[1]      # were created in different moments of the year)
            test_2 = solves[7]
            items.append(Item(first_name, last_name, chall_1, chall_2, test_1, test_2))
    return items


def is_admin(user_id):
    return user_id in admin_list


@bp.route('/', methods=['GET'])
@login_required
def admin():
    db = get_db()
    user_id = session['user_id']
    g.user = read_query(db,
        'SELECT * FROM user WHERE id = %s', (user_id,)
    )[0] 
    token = g.user[TOKEN]
    if is_admin(user_id):
        items = get_itemized_users(db)
        table = ItemTable(items)
        table.border = True
        return render_template('admin.html', table=table)
    else:
        return render_template('cannot_access.html') 
