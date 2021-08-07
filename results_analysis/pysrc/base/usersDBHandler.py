import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
import_dir = os.path.join(dir_path, '../../dbs')
sys.path.insert(1, import_dir)

from db import db
from .utils import fetch_times, generate_vectors
from .config import config_dictionary, set_binary

MIN_TIME = 500
MAX_TIME = 1000000

# The following classes can be ignored if you're working with the pickle files. 
# They basically represent the intermediate layer between the DB and the user classes
# which are the one contained in user_classes.py and that actually represent the 
# different users who got enrolled in our experiments

class UserDBHandler(db):
    
    def __init__(self, challenge_id, db_name, user_id):
        super().__init__(db_name)
        self.challenge_id = challenge_id
        self.db = db_name
        self.user_id = user_id
        self.events = []
        self.level = None


    def fetch_events(self):
        self.events = self.get_events_by_user(self.user_id, self.challenge_id)
        return self.events

    
    def process_events(self):
        if len(self.events) == 0:
            self.fetch_events()
        set_binary(self.challenge_id)
        views, addresses, _, transitions = fetch_times(self.events)
        _, _, deltas = generate_vectors(self.events, False, True, self.challenge_id)
        solution_time = self.compute_solution_time(deltas)
        return views, addresses, solution_time, transitions, self.events


    def compute_solution_time(self, deltas):
        solution_time = 0
        for delta in deltas:
            if delta >= MIN_TIME and delta <= MAX_TIME:
                solution_time += delta
        return solution_time
        

    def get_level(self):
        self.level = self.get_level_by_user(self.user_id)
        return self.level

        

class UserHandlers():
    
    def __init__(self, original_kind):
        self.original_kind = original_kind
        self.all_users = {'1' : [], '7' : []}

    def collect_users_from_db(self, challenge_id, db_name, user_ids):
        for uid in user_ids:
            self.all_users[challenge_id].append(UserDBHandler(challenge_id, db_name, uid))

    def join_challs_by_user(self):
        #assert(len(self.all_users['1']) == len(self.all_users['7']))
        if (len(self.all_users['1']) != len(self.all_users['7'])):
            print("[Warning] In the `{0}` category, we have different num of users for the two challs ({1} vs {2})".format(self.original_kind, len(self.all_users['1']), len(self.all_users['7'])))
        for user_1, user_7 in zip(self.all_users['1'], self.all_users['7']):
            yield user_1, user_7
        
