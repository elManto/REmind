#!/usr/bin/env python

from base.pickle_loader import load_splitted_by_redefinition, load, dump_p_values
from base.initialize import setup_redefinition, reputation_heuristic
from base.bb_classes import NodeType
from statistics import median
from scipy.stats import pearsonr
import numpy as np
import argparse
import os
import matplotlib.pyplot as plt

dir_path = os.path.dirname(os.path.realpath(__file__))
PICKLE_P_VALUES = os.path.join(dir_path, '../pickle/p_values.p')
NOVICE_COLOR = '#36a1ff'
EXPERT_COLOR = '#ff8336'
GET_MIN = lambda a : (a / 60.0) / 1000.0
BBS = 155



DESCR = """Speed analysis"""
opt = argparse.ArgumentParser(description = DESCR)
opt.add_argument("--db", help = "Extract data directly from db, if not set it uses the pickle", action = 'store_true', required = False)
opt.add_argument("--length_correlations", help = "BBs length correlation measurements", action = 'store_true', required = False)

opt.add_argument("--slow_bbs_correlations", help = "Slowest BBs correlation measurements", action = 'store_true', required = False)
args = opt.parse_args()
   

def filter_bbs(bbs):
    core_bbs = []
    for bb in bbs:
        if int(bb.distance) == 0 and bb.type == 'OTHER':
            core_bbs.append(bb)
    return core_bbs

def correlation_times_2_bb_length(core_bbs, novices, experts):
    bb_novice_times = {'max_time' : [], 'total_time' : [], 'first_time' : []}
    bb_expert_times = {'max_time' : [], 'total_time' : [], 'first_time' : []}
    bbs_length = []

    for bb in core_bbs:
        exp_max_times = []
        exp_total_times = []
        exp_first_times = []
        nov_max_times = []
        nov_total_times = []
        nov_first_times = []

        for user_views in bb.user_views:
            if user_views.is_expert():
                exp_max_times.append(max(user_views.times))
                exp_total_times.append(sum(user_views.times))
                exp_first_times.append(user_views.times[0])
            else:
                nov_max_times.append(max(user_views.times))
                nov_total_times.append(sum(user_views.times))
                nov_first_times.append(user_views.times[0])

        bbs_length.append(int(bb.instructions))
        bb_novice_times['max_time'].append(np.average(nov_max_times))
        bb_novice_times['total_time'].append(np.average(nov_total_times))
        bb_novice_times['first_time'].append(np.average(nov_first_times))

        bb_expert_times['max_time'].append(np.average(exp_max_times))
        bb_expert_times['total_time'].append(np.average(exp_total_times))
        bb_expert_times['first_time'].append(np.average(exp_first_times))

    t, p = pearsonr(bb_expert_times['max_time'],bbs_length)
    dump_p_values(PICKLE_P_VALUES, p)
    print(f"Correlation Expert Max Time   - BB length {t, p}")
    t, p = pearsonr(bb_expert_times['total_time'],bbs_length)
    dump_p_values(PICKLE_P_VALUES, p)
    print(f"Correlation Expert Tot Time   - BB length {t, p}")
    t, p = pearsonr(bb_expert_times['first_time'],bbs_length)
    dump_p_values(PICKLE_P_VALUES, p)
    print(f"Correlation Expert First Time - BB length {t, p}")
    t, p = pearsonr(bb_novice_times['max_time'],bbs_length)
    dump_p_values(PICKLE_P_VALUES, p)
    print(f"Correlation Novice Max Time   - BB length {t, p}")
    t, p = pearsonr(bb_novice_times['total_time'],bbs_length)
    dump_p_values(PICKLE_P_VALUES, p)
    print(f"Correlation Novice Tot Time   - BB length {t, p}")
    t, p = pearsonr(bb_novice_times['first_time'],bbs_length)
    dump_p_values(PICKLE_P_VALUES, p)
    print(f"Correlation Novice First Time - BB length {t, p}")


def get_bb_frequency(bb, frequencies):
    for t in frequencies:
        if t[0] == bb:
            return t[1]
    return None
 
def overall_sol_time(all_bbs):
    exp_sol_time = 0
    nov_sol_time = 0
    for bb in all_bbs:
        for user_views in bb.user_views:
            if user_views.is_expert():
                exp_sol_time += sum(user_views.times)
            else:
                nov_sol_time += sum(user_views.times)
    return GET_MIN(exp_sol_time), GET_MIN(nov_sol_time)
                

def diff_bbs(novice_slow_bbs, expert_slow_bbs, all_bbs):
    frequent_nov_bbs = []
    frequent_exp_bbs = []
    freq_nov = {}
    freq_exp = {}
    for bbs in novice_slow_bbs.values():
        for bb in bbs:
            block = bb[0]
            #time = bb[1]
            if block.address in freq_nov:
                freq_nov[block.address] += 1
            else:
                freq_nov[block.address] = 1

    for bbs in expert_slow_bbs.values():
        for bb in bbs:
            block = bb[0]
            if block.address in freq_exp:
                freq_exp[block.address] += 1
            else:
                freq_exp[block.address] = 1

    frequent_nov_bbs = [(k,v) for k,v in freq_nov.items()]
    frequent_exp_bbs = [(k,v) for k,v in freq_exp.items()]
    frequent_nov_bbs.sort(key = lambda a : a[1], reverse = True)
    frequent_exp_bbs.sort(key = lambda a : a[1], reverse = True)

    print("Novice (freq)\t-\tExpert (freq):\n")
    for i,j in zip(frequent_nov_bbs, frequent_exp_bbs):
        print(f"{i[0]} ({i[1]})\t-\t{j[0]} ({j[1]})")


    print("\nDiff")
    nov_bbs_set = set([bb[0] for bb in frequent_nov_bbs])
    exp_bbs_set = set([bb[0] for bb in frequent_exp_bbs])

    exp_sol_time, nov_sol_time = overall_sol_time(all_bbs)
    
    print("BBs present only in novices")
    novices_only = 0
    for bb in (nov_bbs_set - exp_bbs_set):
        time_spent_on_bb = GET_MIN(time_spent_by_bb(bb, all_bbs, False))
        novices_only += time_spent_on_bb
        freq = get_bb_frequency(bb, frequent_nov_bbs)
        if freq == None:
            print("ERROR: freq is None")
        print(f"\n{bb} - {time_spent_on_bb} - {freq}")
        grep_bb(all_bbs, bb)

    print("==========================")
    print("BBs present only in experts")
    for bb in (exp_bbs_set - nov_bbs_set):
        time_spent_on_bb = GET_MIN(time_spent_by_bb(bb, all_bbs, True))
        print(f"{bb} - {time_spent_on_bb}")
        grep_bb(all_bbs,bb)

    print("=========================")
    print("BBs in common")
    percentage_exp = 0
    percentage_nov = 0
    nov_bbs_set = set([bb[0] for bb in frequent_nov_bbs if bb[1] > 4])
    exp_bbs_set = set([bb[0] for bb in frequent_exp_bbs if bb[1] > 4])

    for bb in (nov_bbs_set.intersection(exp_bbs_set)):
        exp_time = GET_MIN(time_spent_by_bb(bb, all_bbs, True))
        nov_time = GET_MIN(time_spent_by_bb(bb, all_bbs, False))
        print(f"{bb} - E: {exp_time} - N: {nov_time}")
        percentage_exp += exp_time 
        percentage_nov += nov_time

    print(f"Percentages: experts {percentage_exp/exp_sol_time} | novices {percentage_nov/nov_sol_time}")
    print(f"Novices only percentage: {novices_only / nov_sol_time}")
        


def time_spent_by_bb(bb_addr, bbs, is_expert):
    exp_time = 0
    nov_time = 0
    for bb in bbs:
        if bb.address == bb_addr:
            for user_views in bb.user_views:
                if user_views.is_expert():
                    exp_time += sum(user_views.times)
                else:
                    nov_time += sum(user_views.times)
    if is_expert:   
        return exp_time
    return nov_time

        

def grep_bb(all_bbs, target_addr):
    for bb in all_bbs:
        if bb.address == target_addr:
            print(f"Task: {bb.task}", end=",")
            print(f"Len: {bb.instructions}", end=",")
            print(f"Type: {bb.type}")

        
            
            
def slow_bbs_correlations(bbs, novices, experts):
    novice_slow_bbs = {n.user_id : [] for n in novices}
    expert_slow_bbs = {n.user_id : [] for n in experts}

    TOP_BBS = int(BBS * 5 / 100)
    
    for bb in bbs:

        for user_views in bb.user_views:
            #tot_time = sum(user_views.times)
            tot_time = max(user_views.times)
            if user_views.is_expert():
                expert_slow_bbs[user_views.uid].append((bb,tot_time))
            else:
                novice_slow_bbs[user_views.uid].append((bb,tot_time))

    for k,val in novice_slow_bbs.items():
        val.sort(key = lambda x : x[1], reverse = True)
        novice_slow_bbs[k] = val[0 : TOP_BBS]
        
    for k,val in expert_slow_bbs.items():
        val.sort(key = lambda x : x[1], reverse = True)
        expert_slow_bbs[k] = val[0 : TOP_BBS]

    diff_bbs(novice_slow_bbs, expert_slow_bbs, bbs)

    return

           
def main():
    if args.db:
        #novices, experts, _ = setup_redefinition()
        print("Not available for now")
        return
    else:
        novices, experts = load_splitted_by_redefinition(os.path.join(dir_path, '../pickle/users_data.p'))
        bbs = load(os.path.join(dir_path, '../pickle/basic_blocks.p'))

    if args.length_correlations:
        core_bbs = filter_bbs(bbs)
        correlation_times_2_bb_length(bbs, novices, experts)

    if args.slow_bbs_correlations:
        #core_bbs = filter_bbs(bbs)
        slow_bbs_correlations(bbs, novices, experts)
        

if __name__ == '__main__':
    main()
