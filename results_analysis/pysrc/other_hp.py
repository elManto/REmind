#!/usr/bin/env python

from base.pickle_loader import load_splitted_by_redefinition, load, dump_p_values
from base.initialize import setup_redefinition, reputation_heuristic
from base.bb_classes import NodeType
from statistics import median
from scipy.stats import pearsonr, mode, iqr
import numpy as np
import argparse
import os
import matplotlib.pyplot as plt
from patterns_analysis import collect_times

dir_path = os.path.dirname(os.path.realpath(__file__))
PICKLE_P_VALUES = os.path.join(dir_path, '../pickle/p_values.p')
NOVICE_COLOR = '#36a1ff'
EXPERT_COLOR = '#ff8336'
GET_MIN = lambda a : (a / 60.0) / 1000.0
BBS = 155



DESCR = """Speed analysis"""
opt = argparse.ArgumentParser(description = DESCR)
opt.add_argument("--db", help = "Extract data directly from db, if not set it uses the pickle", action = 'store_true', required = False)

args = opt.parse_args()
   

def filter_bbs(bbs):
    core_bbs = []
    for bb in bbs:
        if int(bb.distance) > 0 and bb.type != 'OTHER':
            core_bbs.append(bb)
    return core_bbs

def correlation_first_max_tot(bbs, novices, experts):
        novice_ids2bbs = {k : {'Tfirst' : [], 'Tmax' : [], 'Ttot' : []} for k in [u.user_id for u in novices]}
        expert_ids2bbs = {k : {'Tfirst' : [], 'Tmax' : [], 'Ttot' : []} for k in [u.user_id for u in experts]}
        print("IGNORE THE FOLLOWING VALUES FOR THESE EVALUATION")
        nov_median, exp_median = collect_times(bbs, novice_ids2bbs, expert_ids2bbs, False)
        print("FOLLOWING VALUES INSTEAD ARE MEANINGFUL")
         

        t, p = pearsonr(exp_median['Tfirst'] ,exp_median['Tmax'])
        dump_p_values(PICKLE_P_VALUES, p)
        print(f"Expert Tfirst and Tmax {t, p}")

        t, p = pearsonr(exp_median['Tfirst'] ,exp_median['Ttot'])

        dump_p_values(PICKLE_P_VALUES, p)
        print(f"Expert Tfirst and Ttot {t, p}")

        t, p = pearsonr(nov_median['Tfirst'] ,nov_median['Tmax'])
        dump_p_values(PICKLE_P_VALUES, p)
        print(f"Novice Tfirst and Tmax {t, p}")

        t, p = pearsonr(nov_median['Tfirst'] ,nov_median['Ttot'])
        dump_p_values(PICKLE_P_VALUES, p)
        print(f"Novice Tfirst Ttot {t, p}")
    

def correlation_times_2_bb_length(bbs, novices, experts):
    bb_novice_times = {'glances' : [], '1q' : [] , 'avg' : [], '3q' : [], 'mode' : [], 'IQR' : []}
    bb_expert_times = {'glances' : [], '1q' : [] , 'avg' : [], '3q' : [], 'mode' : [], 'IQR' : []}
    bbs_length = []

    for bb in bbs:
        exp_1q = []
        exp_avg = []
        exp_3q = []
        exp_mode = []
        exp_glance = []
        exp_iqr = []

        nov_1q = []
        nov_avg = []
        nov_3q = []
        nov_mode = []
        nov_glance = []
        nov_iqr = []

        for user_views in bb.user_views:
            if user_views.is_expert():
                exp_1q.append(np.quantile(user_views.times, .25))                
                exp_avg.append(np.average(user_views.times))
                exp_3q.append(np.quantile(user_views.times, .75))
                exp_mode.append(mode(user_views.times))
                exp_glance.append(len([glance for glance in user_views.times if glance < 2000]))
                exp_iqr.append(iqr(user_views.times))

            else:
                nov_1q.append(np.quantile(user_views.times, .25))                
                nov_avg.append(np.average(user_views.times))
                nov_3q.append(np.quantile(user_views.times, .75))
                nov_mode.append(mode(user_views.times))
                nov_glance.append(len([glance for glance in user_views.times if glance < 2000]))
                nov_iqr.append(iqr(user_views.times))

        bbs_length.append(int(bb.distance))
        bb_novice_times['1q'].append(np.average(nov_1q))
        bb_novice_times['avg'].append(np.average(nov_avg))
        bb_novice_times['3q'].append(np.average(nov_3q))
        bb_novice_times['mode'].append(np.average(nov_mode))
        bb_novice_times['glances'].append(np.average(nov_glance))
        bb_novice_times['IQR'].append(np.average(nov_iqr))

        bb_expert_times['1q'].append(np.average(exp_1q))
        bb_expert_times['avg'].append(np.average(exp_avg))
        bb_expert_times['3q'].append(np.average(exp_3q))
        bb_expert_times['mode'].append(np.average(exp_mode))
        bb_expert_times['glances'].append(np.average(exp_glance))
        bb_expert_times['IQR'].append(np.average(exp_iqr))


    for key in bb_expert_times:
        t, p = pearsonr(bb_expert_times[key],bbs_length)
        dump_p_values(PICKLE_P_VALUES, p)
        print(f"Correlation Expert {key}   - BB length {t, p}")

    for key in bb_novice_times:
        t, p = pearsonr(bb_novice_times[key],bbs_length)
        dump_p_values(PICKLE_P_VALUES, p)
        print(f"Correlation Novice {key}   - BB length {t, p}")




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

def correlation_skimmed_bbs(bbs, novices, experts):
    threshold = 2000.0
    novice_ids2skimmed = {k : 0 for k in [u.user_id for u in novices]}
    expert_ids2skimmed = {k : 0 for k in [u.user_id for u in experts]}

    for bb in bbs:
        for user_views in bb.user_views:
            if len(user_views.times) >2 and user_views.times[0] < threshold and user_views.times[1] > threshold*10:
                if user_views.is_expert():
                    expert_ids2skimmed[user_views.uid] += 1
                else:
                    novice_ids2skimmed[user_views.uid] += 1
    exp_sol_times = [u.get_visited_bbs() for u in experts]
    nov_sol_times = [u.get_visited_bbs() for u in novices]

    t, p = pearsonr([skimmed_bbs for skimmed_bbs in expert_ids2skimmed.values()], exp_sol_times)
    dump_p_values(PICKLE_P_VALUES, p)
    print(f"Experts Skimmed BBs and solution time {t, p}")

    t, p = pearsonr([skimmed_bbs for skimmed_bbs in novice_ids2skimmed.values()], nov_sol_times)
    dump_p_values(PICKLE_P_VALUES, p)
    print(f"Novices Skimmed BBs and solution time {t, p}")


def correlation_visit_categorization(bbs, novices, experts):
    def visit_categorization(user):
        all_views = user.chall['1'].views + user.chall['7'].views
        short_view = np.quantile(all_views, .25)
        long_view =  np.quantile(all_views, .75)
        short_visits, medium_visits, long_visits = 0, 0, 0
        for view in all_views:
            if view < short_view:
                short_visits += 1
            elif view >= short_view and view < long_view:
                medium_visits += 1
            else:
                long_visits += 1
        return short_visits, medium_visits, long_visits

    nov = {'short' : [], 'medium' : [], 'long' : [], 'time' : []}
    exp = {'short' : [], 'medium' : [], 'long' : [], 'time' : []}

    for user in novices:
        visits = visit_categorization(user)
        nov['short'].append(visits[0])
        nov['medium'].append(visits[1])
        nov['long'].append(visits[2])
        nov['time'].append(user.get_solution_time())

    for user in experts:
        visits = visit_categorization(user)
        exp['short'].append(visits[0])
        exp['medium'].append(visits[1])
        exp['long'].append(visits[2])
        exp['time'].append(user.get_solution_time())

    for key in ['medium', 'long']:
        t, p = pearsonr(exp[key], exp['short'])
        dump_p_values(PICKLE_P_VALUES, p)
        print(f"Expert correlation {key} - sol_time : {t, p}")

        t, p = pearsonr(nov[key], nov['short'])
        dump_p_values(PICKLE_P_VALUES, p)
        print(f"Novice correlation {key} - sol_time : {t, p}")


    

    
    
    
        

def grep_bb(all_bbs, target_addr):
    for bb in all_bbs:
        if bb.address == target_addr:
            print(f"Task: {bb.task}", end=",")
            print(f"Len: {bb.instructions}", end=",")
            print(f"Type: {bb.type}")

        
                  
def main():
    if args.db:
        #novices, experts, _ = setup_redefinition()
        print("Not available for now")
        return
    else:
        novices, experts = load_splitted_by_redefinition(os.path.join(dir_path, '../pickle/users_data.p'))
        bbs = load(os.path.join(dir_path, '../pickle/basic_blocks.p'))


    core_bbs = filter_bbs(bbs)
    correlation_times_2_bb_length(core_bbs, novices, experts)
    correlation_first_max_tot(bbs, novices, experts)
    correlation_skimmed_bbs(bbs, novices, experts)
       

if __name__ == '__main__':
    main()
