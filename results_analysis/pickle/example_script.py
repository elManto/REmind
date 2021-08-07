import pickle
import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
import_dir = os.path.join(dir_path, '../pysrc/')
sys.path.insert(1, import_dir)

# Classes to refer to work with the loaded pickle
from base.bb_classes import NodeType, UserViews, BB



times = {'EXPERTS13' : 0, 'EXPERTS9' : 0, 'NOVICES25' : 0}

def load(path = './basic_blocks.p'):
    with open(path, 'rb') as f:
        all_bbs = pickle.load(f)
        return all_bbs


all_bbs = load()
for bb in all_bbs:
    for user_views in bb.user_views:
        if user_views.uid in times and bb.task == '1':
            #times[user_views.uid] += (sum(user_views.times) / 1000.0) / 60.0

            times[user_views.uid] += (len(user_views.times))
print(times)
            

        
