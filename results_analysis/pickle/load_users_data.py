import pickle
import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
import_dir = os.path.join(dir_path, '../pysrc/')
sys.path.insert(1, import_dir)

# Classes to refer to work with the loaded pickle
from base.user_classes import AllUsers, ChallengeStatistics, User, UserKind

def load(path = './users_data.p'):
    with open(path, 'rb') as f:
        all_users = pickle.load(f)
        return all_users


all_users = load()
experts = [u for u in all_users.all_users if u.redefinition == UserKind.EXPERT]
novices = [u for u in all_users.all_users if u.redefinition == UserKind.NOVICE]
#import ipdb; ipdb.set_trace() 
import IPython; IPython.embed()
