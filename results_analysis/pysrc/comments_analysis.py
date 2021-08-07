#!/usr/bin/env python

from base.pickle_loader import load_splitted_by_redefinition, dump_p_values
from base.initialize import setup_redefinition, reputation_heuristic
from base.user_classes import UserKind
import argparse
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
PICKLE_P_VALUES = os.path.join(dir_path, '../pickle/p_values.p')

NOVICE_COLOR = '#36a1ff'
EXPERT_COLOR = '#ff8336'
GET_MIN = lambda a : (a / 60.0) / 1000.0

LEVELS_TO_FREQ = {
    1 : 'Never',
    2 : 'Sometimes',
    3 : 'Often',
    4 : 'Usually'
}

DESCR = """Analysis of the comments"""
opt = argparse.ArgumentParser(description = DESCR)
opt.add_argument("--db", help = "Extract data directly from db, if not set it uses the pickle", action = 'store_true', required = False)
opt.add_argument("--comments", help = "Comments/Renames stats", action = 'store_true', required = False)
args = opt.parse_args()


def filter_events(raw_events):
    statistics = [0] * 3    # [comment, var_rename, fcn_rename]
    last_comment = 0
    start = raw_events[0]['timestamp']
    end = raw_events[-1]['timestamp']
    for e in raw_events:
        ev_type = e['event']
        if ev_type == 'comment':
            statistics[0] += 1
            last_comment = e['timestamp']
        elif ev_type == 'rename':
            statistics[1] += 1
            last_comment = e['timestamp']
        elif ev_type == 'func_rename':
            statistics[2] += 1
            last_comment = e['timestamp']
        else:
            continue
    
    time_threshold = 0.0
    if last_comment != 0:
        time_threshold = (end - start) / (last_comment - start)
    return statistics, time_threshold


def compute_2_sample_t_test(novices, experts):
    from scipy.stats import ttest_ind
    t, p = ttest_ind(experts, novices, equal_var = False)

    dump_p_values(PICKLE_P_VALUES, p)
    print(f"t: {t}")
    print(f"p-value : {p}")


def collect_comments(users, chall_ids = ['1']):
    import numpy as np

    expert_stats = [0] * 3
    novice_stats = [0] * 3
    experts_data = {'comments' : [], 'rename' : [],  'func_rename' : []}
    novices_data = {'comments' : [], 'rename' : [],  'func_rename' : []}
    tot_exp = 0
    tot_nov = 0
    user_under_threshold = 0
    for user in users:
        for chall_id in chall_ids:
            raw_events = user.chall[chall_id].raw_events
            statistics, last_comment = filter_events(raw_events)
            comments = statistics[0]
            rename = statistics[1]
            func_rename = statistics[2]
            if user.redefinition == UserKind.EXPERT:
                tot_exp += 1
                for i in range(len(statistics)):
                    expert_stats[i] += statistics[i]
                experts_data['comments'].append(comments)
                experts_data['rename'].append(rename)
                experts_data['func_rename'].append(func_rename)
                #experts_data['time'].append(user.get_solution_time(chall_id))
            else:
                tot_nov += 1
                for i in range(len(statistics)):
                    novice_stats[i] += statistics[i]
                novices_data['comments'].append(comments)
                novices_data['rename'].append(rename)
                novices_data['func_rename'].append(func_rename)
                #novices_data['time'].append(user.get_solution_time(chall_id))
            
            if user_under_threshold < last_comment:
                user_under_threshold = last_comment
            

    print("Experts:")
    print(f"\tcomments:    {expert_stats[0]/tot_exp}")
    print(f"\tvar renames: {expert_stats[1]/tot_exp}")
    print(f"\tfcn renames: {expert_stats[2]/tot_exp}")
    print("\nNovices:")
    print(f"\tcomments:    {novice_stats[0]/tot_nov}")
    print(f"\tvar renames: {novice_stats[1]/tot_nov}")
    print(f"\tfcn renames: {novice_stats[2]/tot_nov}")

    print(f"\n\nMax time to comment/rename: {user_under_threshold}")

    print("2 sample t-test time")
    for k in experts_data:
        vector_experts = experts_data[k]
        vector_novices = novices_data[k]
        compute_2_sample_t_test(vector_novices, vector_experts)
        


    
               


def main():
    if args.db:
        novices, experts, _ = setup_redefinition()
    else:
        novices, experts = load_splitted_by_redefinition(os.path.join(dir_path, '../pickle/users_data.p'))

    if args.comments:
        collect_comments(novices + experts)

if __name__ == '__main__':
    main()
