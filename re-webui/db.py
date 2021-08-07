from .config import get_db_config
import mysql.connector
from mysql.connector import Error

from flask import current_app, g
from flask.cli import with_appcontext

conf = get_db_config()
db_name = conf['db_name']
username = conf['username']
pswd = conf['password']
host_name = 'localhost'

def get_db():
    if 'db' not in g:
        try:
            conn = mysql.connector.connect(host=host_name, database=db_name, user=username, password=pswd)
            g.db = conn
        except Error as E:
            print("Error while connecting to MySQL")
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)


def read_query(db, query, val):
    cursor = db.cursor()
    if val != None:
        cursor.execute(query, val)
    else:
        cursor.execute(query)
    res = cursor.fetchall()
    cursor.close()
    return res


def write_query(db, query, val):
    cursor = db.cursor()
    cursor.execute(query, val) 
    db.commit()
    cursor.close()


def register_user(db, val):
    q = 'INSERT INTO user (lev, token, tmp_token, solves, first_name, last_name, other) VALUES (%s, %s, %s, %s, %s, %s, %s)'
    write_query(db, q, val)


def store_solution(db, val):
    q = 'INSERT INTO solutions (user_id, challenge, solution) values(%s, %s, %s)'
    write_query(db, q, val)

def fetch_solutions(db, val):
    q = 'SELECT * FROM solutions WHERE user_id = %s GROUP BY challenge'
    return read_query(db, q, val)


def fetch_all_users(db):
    q = 'SELECT * FROM user'
    return read_query(db, q, None)


def update_tmp_token(db, val):
    q = 'UPDATE user SET tmp_token = %s WHERE id = %s'
    write_query(db, q, val)


def fetch_user_by_id(db, val):
    q = 'SELECT * FROM user WHERE id = %s'
    return read_query(db, q, val)


def fetch_user_by_tmp_token(db, val):
    q = 'SELECT * FROM user WHERE tmp_token = %s'
    return read_query(db, q, val)


def store_new_function_name(db, val):
    q = 'INSERT INTO func (user_id, old_name, new_name, challenge) VALUES (%s, %s, %s, %s)'
    write_query(db, q, val)


def fetch_functions_by_id(db, val):
    q = 'SELECT * FROM func WHERE user_id = %s AND challenge = %s'
    return read_query(db, q, val)


def store_notes(db, val):
    q = 'INSERT INTO notes (user_id, challenge, note) VALUES (%s, %s, %s)'
    write_query(db, q, val)


def fetch_notes(db, val):
    q = 'SELECT * FROM notes WHERE user_id = %s AND challenge = %s ORDER BY id DESC LIMIT 1'
    return read_query(db, q, val)


def store_events(db, val):
    q = 'INSERT INTO events (user_id, challenge, fcn_name, event) VALUES (%s, %s, %s, %s)'
    write_query(db, q, val)


def fetch_events(db, val):
    q = 'SELECT event FROM events WHERE user_id = %s AND challenge = %s AND fcn_name = %s'
    return read_query(db, q, val)
