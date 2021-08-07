import pickle
import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
import_dir = os.path.join(dir_path, '../pysrc/')
sys.path.insert(1, import_dir)

# Classes to refer to work with the loaded pickle
from base.bb_classes import NodeType, UserViews, BB

def load(path = './basic_blocks.p'):
    with open(path, 'rb') as f:
        all_bbs = pickle.load(f)
        return all_bbs


all_bbs = load()
import ipdb; ipdb.set_trace()
        
