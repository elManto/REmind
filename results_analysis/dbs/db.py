import sqlite3
import json
import mysql.connector

#challenge_code=1
GET_EVENTS = "SELECT event FROM events WHERE user_id = {0} AND challenge = {0}"
GET_EVENTS_ENTRY = "SELECT * FROM events WHERE user_id = {0} AND challenge = {0}"
GET_FUNCTIONS_ORDER = "SELECT fcn_name FROM events WHERE user_id = {0} AND challenge = {0}"
GET_USERS = "SELECT user_id, solution FROM solutions WHERE CHALLENGE = {0} GROUP BY user_id"
GET_LEVEL_FROM_USER = "SELECT lev FROM user WHERE id = {0}"
GET_REGISTRATION = "SELECT * FROM user WHERE id = {0}"


class db:
    def __init__(self, db_name, db_type='mysql'):
        if db_type == 'mysql':
            self.conn = mysql.connector.connect(host='localhost', database=db_name, user='mantovan', password='21password21')
        else:
            self.conn = sqlite3.connect(db_name)
        self.type = db_type
        self.name = db_name

    def mysql_read_query(self, query, val):
        cursor = self.conn.cursor()
        if val != None:
            cursor.execute(query, val)
        else:
            cursor.execute(query)
        res = cursor.fetchall()
        cursor.close()
        return res

    def mysql_write_query(self, query, val):
        cursor = self.conn.cursor()
        if val != None:
            cursor.execute(query, val)
        else:
            cursor.execute(query)
        self.conn.commit()
        cursor.close()   
    
    def sqlite_read_query(self, query, val):
        res = self.conn.execute(query, val).fetchall()
        return res
    
    
    def read_query(self, template, val):
        query = self.generate_query_string(template)
        if self.type == 'mysql':
            return self.mysql_read_query(query, val)
        else:
            return self.sqlite_read_query(query, val)


    def generate_query_string(self, string):
        res = string.format('?') if self.type == 'sqlite' else string.format('%s')
        return res

    
    def get_registration_data(self, user_id):
        res = self.read_query(GET_REGISTRATION, (user_id,))[0]
        return res


    def get_functions_visited(self, user_id, challenge_code, freq = False):
        res = self.read_query(GET_FUNCTIONS_ORDER, (user_id, challenge_code))
        fcns = [res[0][0]]
        if not freq:
            for tup in res:
                fcn = tup[0]
                if fcns[-1] != fcn:
                    fcns.append(fcn)
        else:
            fcns = [(res[0][0], 1)]
            for tup in res:
                fcn = tup[0]
                if fcns[-1][0] != fcn:
                    t = (fcn, 1)
                    fcns.append(t)
                else:
                    t = fcns.pop()
                    new_t = (t[0], t[1] + 1)
                    fcns.append(new_t)
        return fcns 

    
    def get_events_by_user(self, user_id, challenge_code):
        res = self.read_query(GET_EVENTS, (user_id, challenge_code))
        events = [json.loads(row[0]) for row in res]
        return events

    def get_events_entry_by_user(self, user_id, challenge_code):
        res = self.read_query(GET_EVENTS_ENTRY, (user_id, challenge_code))
        return res


    def get_interesting_users(self, challenge_code):
        res = self.read_query(GET_USERS, (challenge_code, ))
        ids = []
        for row in res:
            if row [1] != '':
                ids.append(row[0])
        return ids


    def store_results(self, user_id, results):
        json_data = json.dumps(results)
        self.conn.execute("INSERT INTO result (user_id, json_data) VALUES (?, ?)", (user_id, json_data))
        self.conn.commit()


    def get_events_by_type(self, user_id, challenge_code, event_type):
        events = self.get_events_by_user(user_id, challenge_code)
        return [ev for ev in events if ev['event'] == event_type]


    def get_level_by_user(self, id):
        level = self.read_query(GET_LEVEL_FROM_USER, (id, ))[0][0]
        return level

    def register_user(self, val):
        q = 'INSERT INTO user (lev, token, tmp_token, solves, first_name, last_name, other) VALUES (%s, %s, %s, %s, %s, %s, %s)'
        self.mysql_write_query(q, val)

    def store_solution(self, val):
        q = 'INSERT INTO solutions (user_id, challenge, solution) values(%s, %s, %s)'
        self.mysql_write_query(q, val)


    def store_new_function_name(self, val):
        q = 'INSERT INTO func (user_id, old_name, new_name, challenge) VALUES (%s, %s, %s, %s)'
        self.mysql_write_query(q, val)


    def store_notes(self, val):
        q = 'INSERT INTO notes (user_id, challenge, note) VALUES (%s, %s, %s)'
        self.mysql_write_query(q, val)

    def store_events(self, val):
        q = 'INSERT INTO events (user_id, challenge, fcn_name, event) VALUES (%s, %s, %s, %s)'
        self.mysql_write_query(q, val)

    def get_last_inserted_user(self):
        q = 'select id from user order by id desc limit 1'
        return self.read_query(q, None)[0][0]

    def get_solution_entry(self, user_id, challenge_id):
        q = 'SELECT * FROM solutions WHERE user_id = {0} and challenge = {0}'
        return self.read_query(q, (user_id, challenge_id))[0]
