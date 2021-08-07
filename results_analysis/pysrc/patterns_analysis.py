#!/usr/bin/env python

from base.pickle_loader import load_splitted_by_redefinition, load, dump_p_values
from base.initialize import setup_redefinition, reputation_heuristic
from statistics import median
import numpy as np
import argparse
import os
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

dir_path = os.path.dirname(os.path.realpath(__file__))
PICKLE_P_VALUES = os.path.join(dir_path, '../pickle/p_values.p')
NOVICE_COLOR = '#36a1ff'
EXPERT_COLOR = '#ff8336'
GET_MIN = lambda a : (a / 60.0) / 1000.0
BBS = 155



DESCR = """Analysis of the Tfirst/Tmax to visit BBs"""
opt = argparse.ArgumentParser(description = DESCR)
opt.add_argument("--db", help = "Extract data directly from db, if not set it uses the pickle", action = 'store_true', required = False)
opt.add_argument("--median_times", help = "Plot figure 9, and compute Tfirst,max,tot metrics and 2-sample t-test", action = 'store_true', required = False)
opt.add_argument("--glances", help = "Glances i.e. visits under 2 seconds", action = 'store_true', required = False)
opt.add_argument("--average_bbs", help = "Avg num of BBs visited", action = 'store_true', required= False)
opt.add_argument("--visits", help = "Figure 11 and related data", action = 'store_true', required = False)
opt.add_argument("--correlation_multiple_visits", help = "Correlation multiple visited BBs with solution time", action = 'store_true', required = False)

#opt.add_argument("--sum", help = "Cumulative time", action = 'store_true', required = False)
args = opt.parse_args()

def correlation_multiple_visited_bbs(bbs, novices, experts):
    novice_ids2bbs = {k : 0 for k in [u.user_id for u in novices]}
    expert_ids2bbs = {k : 0 for k in [u.user_id for u in experts]}

    for bb in bbs:
        for user_view in bb.user_views:
            if len(user_view.times) > 1:
                if user_view.is_expert():
                    expert_ids2bbs[user_view.uid] += 1
                else:
                    novice_ids2bbs[user_view.uid] += 1
    
    # test correlation with solution times
    novice_sol_times = []
    novice_multiple_visited_bbs = []
    for u in novices:
        sol_time = u.get_solution_time()
        multiple_visits = novice_ids2bbs[u.user_id]
        novice_sol_times.append(sol_time)
        novice_multiple_visited_bbs.append(multiple_visits)

    expert_sol_times = []       
    expert_multiple_visited_bbs = []
    for u in experts:
        sol_time = u.get_solution_time()
        multiple_visits = expert_ids2bbs[u.user_id]
        expert_sol_times.append(sol_time)
        expert_multiple_visited_bbs.append(multiple_visits)

    c, p = pearsonr(novice_multiple_visited_bbs, novice_sol_times)
    dump_p_values(PICKLE_P_VALUES, p)
    print(f"Novices Correlation Multiple visited BBs - SOl time {c, p}")
    c, p = pearsonr(expert_multiple_visited_bbs, expert_sol_times)
    dump_p_values(PICKLE_P_VALUES, p)
    print(f"Experts Correlation Multiple visited BBs - SOl time {c, p}")


def visits_stats(bbs, novices, experts):

    novice_ids2bbs = {k : {'first==max' : 0, 'first==tot' : 0, 'visits' : 0} for k in [u.user_id for u in novices]}
    expert_ids2bbs = {k : {'first==max' : 0, 'first==tot' : 0, 'visits' : 0} for k in [u.user_id for u in experts]}

    for bb in bbs:
        for user_views in bb.user_views:
            visited_once = 0
            visited_more = 0
            visited_much = 0
            Tfirst = user_views.times[0] 
            Ttot = sum(user_views.times)
            Tmax = max(user_views.times)
            uid = user_views.uid 
            if Tfirst == Ttot:
                visited_once = 1
            elif Tfirst == Tmax:
                visited_more = 1
            else:
                visited_much = 1

            if user_views.is_expert():
                expert_ids2bbs[user_views.uid]['first==max'] += visited_more
                expert_ids2bbs[user_views.uid]['first==tot'] += visited_once
                expert_ids2bbs[user_views.uid]['visits'] += visited_much
            else:
                novice_ids2bbs[user_views.uid]['first==max'] += visited_more
                novice_ids2bbs[user_views.uid]['first==tot'] += visited_once
                novice_ids2bbs[user_views.uid]['visits'] += visited_much

    for nov in novices:    
        uid = nov.user_id
        novice_ids2bbs[uid]['first==max'] /= BBS
        novice_ids2bbs[uid]['first==tot'] /= BBS
        novice_ids2bbs[uid]['visits'] /= BBS

    for exp in experts:
        uid = exp.user_id
        expert_ids2bbs[uid]['first==max'] /= BBS
        expert_ids2bbs[uid]['first==tot'] /= BBS

    first_max_experts_list = [expert_ids2bbs[uid]['first==max']*100 for uid in expert_ids2bbs]
    first_max_novices_list = [novice_ids2bbs[uid]['first==max']*100 for uid in novice_ids2bbs]

    first_tot_experts_list = [expert_ids2bbs[uid]['first==tot']*100 for uid in expert_ids2bbs]
    first_tot_novices_list = [novice_ids2bbs[uid]['first==tot']*100 for uid in novice_ids2bbs]

    first_no_longer_novices_list = [ novice_ids2bbs[uid]['visits']*100 for uid in novice_ids2bbs]


    print(f"Median experts Tfirst==Tmax: {median(first_max_experts_list)}")
    print(f"Median novices Tfirst==Tmax: {median(first_max_novices_list)}")
    print(f"Novices' first visit is not the one where they reason longer {median(first_no_longer_novices_list)}")
    import ipdb; ipdb.set_trace()

    plot_visits_stats(first_max_novices_list, first_tot_novices_list, first_max_experts_list, first_tot_experts_list)
    return




def plot_visits_stats(N_X, N_Y, E_X, E_Y):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(E_X, E_Y, alpha=0.8, c="#ff6404", edgecolors='none', s=30, marker="o", label="Experts")
    ax.scatter(N_X, N_Y, alpha=0.8, c="#048aff", edgecolors='none', s=30, marker="o", label="Novices")
    
    plt.xlabel("T_first == T_max")
    plt.ylabel("T_first == T_tot")
    plt.legend()
    # plt.xscale("log")
    # plt.yscale("log")
    fig.savefig("/tmp/first_visit.pdf")
    
    plt.show()


def glance_statistics(bbs, novice_ids, expert_ids):
    experts_once = {k : 0 for k in expert_ids}
    novices_once = {k : 0 for k in novice_ids}
    experts_glances = {k : 0 for k in expert_ids}
    novices_glances = {k : 0 for k in novice_ids}

    for bb in bbs:
        for user_views in bb.user_views:
            discarded = 0
            glance = 0
            Tfirst = user_views.times[0] 
            Ttot = sum(user_views.times)
            uid = user_views.uid 

            if Tfirst == Ttot:
                discarded = 1
                if Tfirst < 2000.0:
                    glance = 1

            if user_views.is_expert():
                experts_once[uid] += discarded
                experts_glances[uid] += glance
            else:
                novices_once[uid] += discarded
                novices_glances[uid] += glance
            
    visited_once_exp = np.average([v for v in experts_once.values()]) 
    visited_once_nov = np.average([v for v in novices_once.values()]) 


    print(f"On avg experts visit {visited_once_exp / BBS} of the BBs once")
    print(f"On avg novices visit {visited_once_nov / BBS} of the BBs once")

    ratio_exp = [num_of_glances / bbs_visited_once for bbs_visited_once, num_of_glances in zip(experts_once.values(), experts_glances.values()) if bbs_visited_once != 0]

    ratio_nov = [num_of_glances / bbs_visited_once for bbs_visited_once, num_of_glances in zip(novices_once.values(), novices_glances.values()) if bbs_visited_once != 0]

    avg_glances_exp = np.average(ratio_exp)
    avg_glances_nov = np.average(ratio_nov)

    bbs_glance_visited_exp = visited_once_exp * avg_glances_exp / BBS
    bbs_glance_visited_nov = visited_once_nov * avg_glances_nov / BBS

    print(f"Expert glances: {avg_glances_exp}")
    print(f"BBs discarded by experts via glances overall: {bbs_glance_visited_exp}")
    print(f"Novice glances: {avg_glances_nov}")
    print(f"BBs discarded by novices via glances overall: {bbs_glance_visited_nov}")

    return


def collect_times(bbs, novice_ids2bbs, expert_ids2bbs, print_out = True):
    novice_median_times = {'Tfirst' : [], 'Tmax' : [], 'Ttot' : []}
    expert_median_times = {'Tfirst' : [], 'Tmax' : [], 'Ttot' : []}

    for bb in bbs:
        for views_per_single_user in bb.user_views:
            Tfirst = views_per_single_user.times[0] / 1000
            Ttot = sum(views_per_single_user.times) / 1000
            Tmax = max(views_per_single_user.times) / 1000
            uid = views_per_single_user.uid
            if views_per_single_user.is_expert():
                expert_ids2bbs[uid]['Tfirst'].append(Tfirst)
                expert_ids2bbs[uid]['Tmax'].append(Tmax)
                expert_ids2bbs[uid]['Ttot'].append(Ttot)
            else:
                novice_ids2bbs[uid]['Tfirst'].append(Tfirst)
                novice_ids2bbs[uid]['Tmax'].append(Tmax)
                novice_ids2bbs[uid]['Ttot'].append(Ttot)

    for expert, times in expert_ids2bbs.items():
        expert_median_times['Tfirst'].append(median(times['Tfirst']))
        expert_median_times['Tmax'].append(median(times['Tmax']))
        expert_median_times['Ttot'].append(median(times['Ttot']))

    for novice, times in novice_ids2bbs.items():
        novice_median_times['Tfirst'].append(median(times['Tfirst']))
        novice_median_times['Tmax'].append(median(times['Tmax']))
        novice_median_times['Ttot'].append(median(times['Ttot']))

    if print_out:
        print("Tfirst")
        print(f"Expert: {np.average(expert_median_times['Tfirst'])}")
        print(f"Novice: {np.average(novice_median_times['Tfirst'])}")
        
            
        print("Tmax")
        print(np.average(expert_median_times['Tmax']))
        print(np.average(novice_median_times['Tmax']))

        print("Ttot")
        print(np.average(expert_median_times['Ttot']))
        print(np.average(novice_median_times['Ttot']))

        print("2-sample t-test Tfirst")
        compute_2_sample_t_test(novice_median_times['Tfirst'], expert_median_times['Tfirst'])
        print("\n2-sample t-test Tmax")
        compute_2_sample_t_test(novice_median_times['Tmax'], expert_median_times['Tmax'])
        print("\n2-sample t-test Ttot")
        compute_2_sample_t_test(novice_median_times['Ttot'], expert_median_times['Ttot'])

    return novice_median_times, expert_median_times


def compute_2_sample_t_test(novices, experts, dump = True):

    from scipy.stats import ttest_ind
    t, p = ttest_ind(novices, experts, equal_var=False)

    if dump:
        dump_p_values(PICKLE_P_VALUES, p)

    print("\n2-sample t-test results")
    print(f"t: {t}")
    print(f"p-value: {p}")


def plot_times(nov_median, exp_median, output_path = '/tmp/median_times.pdf'):
    N_first, N_max, N_tot = nov_median['Tfirst'], nov_median['Tmax'], nov_median['Ttot']

    E_first, E_max, E_tot = exp_median['Tfirst'], exp_median['Tmax'], exp_median['Ttot']

    bp1 = plt.boxplot([N_first, N_max, N_tot], positions = [-0.4, 1.6, 3.6], widths = 0.6, vert=True,  sym='', patch_artist=True, medianprops={'color':'black'})
    bp2 = plt.boxplot([E_first, E_max, E_tot], positions = [0.4, 2.4, 4.4], widths = 0.6, vert=True,  sym='', patch_artist=True, medianprops={'color':'black'})
    
    
    # https://chase-seibert.github.io/blog/2011/07/29/python-calculate-lighterdarker-rgb-colors.html
    def color_variant(hex_color, brightness_offset=1):
        """ takes a color like #87c95f and produces a lighter or darker variant """
        if len(hex_color) != 7:
            raise Exception("Passed %s into color_variant(), needs to be in #87c95f format." % hex_color)
        rgb_hex = [hex_color[x:x+2] for x in [1, 3, 5]]
        new_rgb_int = [int(hex_value, 16) + brightness_offset for hex_value in rgb_hex]
        new_rgb_int = [min([255, max([0, i])]) for i in new_rgb_int] # make sure new values are between 0 and 255    # hex() produces "0x88", we want just "88"
        return "#" + "".join([hex(i)[2:] for i in new_rgb_int])
    
    
    experts_color = color_variant(EXPERT_COLOR, 16)
    novices_color = color_variant(NOVICE_COLOR, 16)
    
    for patch in bp1['boxes']:
            patch.set_facecolor(novices_color)
    for patch in bp2['boxes']:
            patch.set_facecolor(experts_color)
    
    plt.plot([], c=novices_color, label='Novices')
    plt.plot([], c=experts_color, label='Experts')
    plt.legend()
    
    plt.xticks(range(0, 6, 2), ['First', 'Max', 'Total'])
    plt.xlim(-1, 6)
    # plt.ylim(0, 8)
    plt.tight_layout()
    plt.yscale("log")
    
    plt.grid(axis='y')
    plt.ylabel('Median Time (s)')
    
    print(f"Generating plot at {output_path}")
    plt.savefig(output_path)
    

def get_average_bbs(novices, experts):
    nov_visited_bbs = [n.get_visited_bbs() for n in novices]
    exp_visited_bbs = [e.get_visited_bbs() for e in experts]
    exp_avg = np.average(exp_visited_bbs)
    nov_avg = np.average(nov_visited_bbs)
    print(f"Average visited BBs for experts {exp_avg}")
    print(F"Average visited BBs for novices {nov_avg}")
    


           
def main():
    if args.db:
        #novices, experts, _ = setup_redefinition()
        print("Not available for now")
        return
    else:
        novices, experts = load_splitted_by_redefinition(os.path.join(dir_path, '../pickle/users_data.p'))
        bbs = load(os.path.join(dir_path, '../pickle/basic_blocks.p'))


    if args.median_times:
        novice_ids2bbs = {k : {'Tfirst' : [], 'Tmax' : [], 'Ttot' : []} for k in [u.user_id for u in novices]}
        expert_ids2bbs = {k : {'Tfirst' : [], 'Tmax' : [], 'Ttot' : []} for k in [u.user_id for u in experts]}
        nov_median, exp_median = collect_times(bbs, novice_ids2bbs, expert_ids2bbs)
        plot_times(nov_median, exp_median)
    
    if args.glances:
        glance_statistics(bbs, [u.user_id for u in novices], [u.user_id for u in experts])

    if args.average_bbs:
        get_average_bbs(novices, experts)

    if args.visits:
        visits_stats(bbs, novices, experts)

    if args.correlation_multiple_visits:
        correlation_multiple_visited_bbs(bbs, novices, experts)

if __name__ == '__main__':
    main()
