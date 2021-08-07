import pickle
import sys
import os
from .user_classes import AllUsers, ChallengeStatistics, User, UserKind
from .p_values import Pvalues

dir_path = os.path.dirname(os.path.realpath(__file__))

def load(path):
    with open(path, 'rb') as f:
        all_data = pickle.load(f)
        return all_data


def load_splitted_by_original_kind(path):
    all_users = load(path)
    novices, experts = [], []
    for user in all_users.all_users:
        if user.original_kind == UserKind.NOVICE:
            novices.append(user)
        else:
            experts.append(user)
    return novices, experts


def load_splitted_by_redefinition(path):
    all_users = load(path)
    novices, experts = [], []
    for user in all_users.all_users:
        if user.redefinition == UserKind.NOVICE:
            novices.append(user)
        else:
            experts.append(user)
    return novices, experts


def init_p_values(path):
    P = Pvalues()
    with open(path, 'wb') as p_values_pickle:
        pickle.dump(P, p_values_pickle)        


def dump_p_values(path, *args):
    with open(path, 'rb') as p_values_pickle:
        P = pickle.load(p_values_pickle)
        for p in args:
            P.add(p)
        
    with open(path, 'wb') as p_values_pickle:
        pickle.dump(P, p_values_pickle)

def load_p_values(path):
    with open(path, 'rb') as p_values_pickle:
        P = pickle.load(p_values_pickle)
        return P.get_p_values()
 
    
    
    


