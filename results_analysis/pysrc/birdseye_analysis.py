#!/usr/bin/env python

import os
from base.initialize import setup_redefinition
from base.pickle_loader import load, load_splitted_by_redefinition
from base.utils import generate_vectors
import argparse


DESCR = """Birdseye overview analysis"""

opt = argparse.ArgumentParser(description = DESCR)
opt.add_argument("--db", help = "Extracts data from the DB, default is the pickle", action='store_true', required=False)
opt.add_argument("--top_flop", help = "Top vs Flop , Figure 8", action='store_true', required = False)
opt.add_argument("--birdseye", help = "How many users adopt birdseye on avg, Section 6.3", action = 'store_true', required = False)

args = opt.parse_args()


GET_MIN = lambda a : (a / 1000.0) / 60.0
dir_path = os.path.dirname(os.path.realpath(__file__))

def cumulative_bb_visit(user, challenge_id):    
    events = user.chall[challenge_id].raw_events
    bbs_count = []
    time = []
    observed_addr = []
    count = 0
    timeline, addresses, _ = generate_vectors(events, False, True, 1)
    timeline = [GET_MIN(t) for t in timeline]
    ticks = 0
    for t, addr in zip(timeline, addresses):
        ticks += 1
        if addr not in observed_addr:
            observed_addr.append(addr)
            time.append(t)
            count += 1
            bbs_count.append(count)

    return bbs_count, time, observed_addr


def get_vectors_for_plot(user_id, challenge_id):
    code_coverage, timeline, already_visited_bbs = cumulative_bb_visit(user_id, challenge_id)
    blocks_count = len(already_visited_bbs)
    count = 92
    blocks = [c*100.0/count for c in code_coverage]
    #blocks = code_coverage
    max_time = timeline[-1]
    time = [t * 100.0 / max_time for t in timeline]
    return blocks, time 

            
def has_overview(user, challenge_id):
    _, timeline, already_visited_bbs = cumulative_bb_visit(user, challenge_id)
    time_threshold = timeline[0] + ((timeline[-1] - timeline[0]) * 0.30)
    coverage_threshold = len(already_visited_bbs) * 0.70
    count = 0
    for bb, t in zip(already_visited_bbs, timeline):
        count += 1
        if t > time_threshold:
            break
    return count >= coverage_threshold
            

legend_top = False
legend_worst = False
def plot_single_cdf(time, bbs_count, challenge_id, color, lab):

    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.interpolate import interp1d

    x_new = np.linspace(min(time), max(time), 500)
    f = interp1d(time, bbs_count)
    y_smooth=f(x_new)
    if lab == '':
        plt.plot(x_new, y_smooth, c=color)
    else:
        plt.plot(x_new, y_smooth, c=color, label=lab)

    plt.ylim(0, 110)
    plt.xlabel("Time (%)")
    plt.ylabel("Visited BBs (%)")

    return plt

    

def fetch_top_flop(users):
    solution_times_2_id = {u.get_solution_time(): u for u in users}
    solution_times = [time for time in solution_times_2_id.keys()]
    solution_times.sort()
    best = [solution_times_2_id[t] for t in solution_times[0 : 5]]
    worst = [solution_times_2_id[t] for t in solution_times[-5 : ]]
    return best, worst
    

def plot(best, worst, challenge_id, output_path):
    global legend_top
    global legend_worst

    for best_user in best:
        bbs_count, time = get_vectors_for_plot(best_user, challenge_id)
        color = 'r'
        if not legend_top:
            legend_top = True
            label = 'Best'
        else:
            label = ''

        plt = plot_single_cdf(time, bbs_count, challenge_id, color, label)

    for worst_user in worst:
        bbs_count, time = get_vectors_for_plot(worst_user, challenge_id)
        color = 'b'
        if not legend_worst:
            legend_worst = True
            label = 'Worst'
        else:
            label = ''

        plt = plot_single_cdf(time, bbs_count, challenge_id, color, label)
    
    plt.legend()
    plt.savefig(output_path)

       
def get_overview_statistics(users, challenge_id):
    overview = 0
    for u in users:
        if has_overview(u, challenge_id):
            overview += 1

    return round(overview / float(len(users)), 2)
    
if args.db:
    novices, experts, all_users = setup_redefinition()
else:
    novices, experts = load_splitted_by_redefinition(os.path.join(dir_path, '../pickle/users_data.p'))


if args.top_flop:
    # Figure 8 
    challenge_id = '7'
    output_path = "/tmp/top-and-flop.pdf"
    print("Generating output in {0}".format(output_path))
    best, worst = fetch_top_flop(experts)
    plot(best, worst, challenge_id, output_path)

if args.birdseye:
    # Other data of Section 6.3
    #challenge_id = '7'
    nov_2 = get_overview_statistics(novices, '7')
    exp_2 = get_overview_statistics(experts, '7')
    
    #challenge_id = '1'
    nov_1 = get_overview_statistics(novices, '1')
    exp_1 = get_overview_statistics(experts, '1')
    
    print((nov_1 + nov_2) / 2)
    print((exp_1 + exp_2) / 2)



    
