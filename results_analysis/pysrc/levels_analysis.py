#!/usr/bin/env python

from base.pickle_loader import load_splitted_by_redefinition, init_p_values, dump_p_values
from base.initialize import setup_redefinition, reputation_heuristic
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

DESCR = """Analysis of the levels/solution times/transitions"""
opt = argparse.ArgumentParser(description = DESCR)
opt.add_argument("--db", help = "Extract data directly from db, if not set it uses the pickle", action = 'store_true', required = False)
opt.add_argument("--levels", help = "Plot of Figure 4 that correlated users' solution time to their level", action = 'store_true', required = False)
opt.add_argument("--transitions", help = "Plot of Figure 10 that contains the visited BBs w.r.t. the solution times", action = 'store_true', required = False)
opt.add_argument("--sol_times", help = "Computes the avg solution times for expert/novices, as it is used in Section 6", action = 'store_true', required = False)
opt.add_argument("--groups", help = "Computes the avg solution times according to the initial question, thus splitting the results in 4 groups, as it is used in Section 6", action = 'store_true', required = False)
opt.add_argument("--two_sample_test", help = "Compute the 2-sample t-test of the solution times comparing experts and novices", action = 'store_true', required = False)
opt.add_argument("--threshold", help = "Print the time threshold used to separate Experts vs Novices", action = 'store_true', required = False)
opt.add_argument("--sum", help = "Cumulative time", action = 'store_true', required = False)
args = opt.parse_args()

init_p_values(PICKLE_P_VALUES)


def scatter_plot(E_X, E_Y, E_C, N_X, N_Y, N_C, output_path, x_label, y_label):
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(E_X, E_Y, c = E_C, label = "Experts")
    ax.scatter(N_X, N_Y, c = N_C, label = "Novices")
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    print("Plotting image at {0}".format(output_path))
    plt.savefig(output_path)


def plot_levels_seaborn(df, threshold, x_label, y_label, output_path):
    import seaborn as sns
    import matplotlib.pyplot as plt
    colors = [EXPERT_COLOR, NOVICE_COLOR]
    sns.set_palette(sns.color_palette(colors))
    ax = sns.swarmplot(data=df, y="solution_times", x="categories", hue="skill", order=['Never','Sometimes',     'Often','Usually'])

    ax.axhline(threshold, ls='--', color='black', linewidth=1)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.legend(loc='upper right')
    print("Plotting image at {0}".format(output_path))
    plt.savefig(output_path)#, box_inches='tight')
    

def setup_user_vectors(novices, experts):
    E_X = []
    E_Y = []
    E_C = []
    N_X = []
    N_Y = []
    N_C = []
    for user in novices + experts:
        if user in novices:
            N_C.append(NOVICE_COLOR) 
            N_X.append(user.get_level())
            N_Y.append(GET_MIN(user.get_solution_time()))
        else:
            E_C.append(EXPERT_COLOR) 
            E_X.append(user.get_level())
            E_Y.append(GET_MIN(user.get_solution_time()))
    return E_X, E_Y, E_C, N_X, N_Y, N_C



def plot_levels(novices, experts, output_path, simple_scatter_plot = False):
    E_X, E_Y, E_C, N_X, N_Y, N_C = setup_user_vectors(novices, experts)
    x_label = "How often do you reverse ?"
    y_label = "Solution time (min)"
    if simple_scatter_plot:
        scatter_plot(E_X, E_Y, E_C, N_X, N_Y, N_C, output_path, x_label, y_label)
    else:
        # Put the data in the same shape as required by Simo's script
        data = dict()
        data["solution_times"] = E_Y + N_Y
        data["categories"] = [LEVELS_TO_FREQ[E_X[i]] for i in range(len(E_X))] + [LEVELS_TO_FREQ[N_X[i]] for i in range(len(N_X))]
        data["skill"] = ['Expert'] * len(E_X) + ['Novice'] * len(N_X)
        threshold = GET_MIN(get_threshold(novices + experts, print_out = False))
        plot_levels_seaborn(data, threshold, x_label, y_label, output_path)
    return


def plot_visited_bbs(novices, experts, output_path):
    E_X = []
    E_Y = []
    E_C = []
    N_X = []
    N_Y = []
    N_C = []
    for user in novices + experts:
        if user in novices:
            N_C.append(NOVICE_COLOR) 
            N_X.append(GET_MIN(user.get_solution_time()))    # Different info compared to the ones
            N_Y.append(user.get_visited_bbs())      # collected in `setup_user_vectors`
        else:
            E_C.append(EXPERT_COLOR) 
            E_X.append(GET_MIN(user.get_solution_time()))
            E_Y.append(user.get_visited_bbs())

    x_label = "Solution Time (min)"
    y_label = "Number of Visited BBs"
    scatter_plot(E_X, E_Y, E_C, N_X, N_Y, N_C, output_path, x_label, y_label)
    return


def compute_2_sample_t_test(novices, experts):
    _, E_times, _, _, N_times, _ = setup_user_vectors(novices, experts)
    E_bbs = [e.get_visited_bbs() for e in experts]
    N_bbs = [n.get_visited_bbs() for n in novices]
    from scipy.stats import ttest_ind
    t, p = ttest_ind(E_times, N_times, equal_var=False)
    dump_p_values(PICKLE_P_VALUES, p)
    print("Confidence intervals computed with confidence == 0.95")
    conf_exp = mean_confidence_interval(E_times)
    conf_nov = mean_confidence_interval(N_times)
    print(f"Expert: {conf_exp}")
    print(f"Novice: {conf_nov}")
    print("\n2-sample t-test results")
    print(f"t: {t}")
    print(f"p-value: {p}")


    t, p = ttest_ind(N_bbs, E_bbs, equal_var=False)
    dump_p_values(PICKLE_P_VALUES, p)
    print("\n2-sample t-test results w.r.t. BBs (Figure 10)")
    print(f"t: {t}")
    print(f"p-value: {p}")




def mean_confidence_interval(data, confidence=0.95):
    import numpy as np
    import scipy.stats
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h


def compute_average_solution_times(novices, experts):
    import numpy as np
    nov_times = [GET_MIN(nov.get_solution_time()) for nov in novices]
    print(f"Novices:\n\tMin -> {min(nov_times)}\n\tMax -> {max(nov_times)}\n\tAvg -> {np.average(nov_times)}")

    exp_times = [GET_MIN(exp.get_solution_time()) for exp in experts]
    print(f"Experts:\n\tMin -> {min(exp_times)}\n\tMax -> {max(exp_times)}\n\tAvg -> {np.average(exp_times)}")
    

def compute_average_solution_times_by_group(novices, experts):
    import numpy as np
    groups = {k : [] for k in range(1, 5)}
    for u in novices + experts:
        groups[int(u.get_level())].append(GET_MIN(u.get_solution_time()))

    for level, times in groups.items():
        print(f"Level {level} -> avg : {np.average(times)}")
    return 0


def get_threshold(users, print_out = True):
    threshold = 0
    for user in users:
        if user.get_solution_time() > threshold and user.level >= 3:
            threshold = user.get_solution_time()
    redef_novices = 0
    redef_experts = 0
    for user in users:
        if user.get_solution_time() > threshold:
            redef_novices += 1
        else:
            redef_experts += 1
    if print_out:
        print(f"Threshold -> {GET_MIN(threshold)}")
        print(f"Novices after redefinition -> {redef_novices}")
        print(f"Experts after redefinition -> {redef_experts}")
    return threshold
    
def cumulative(users):
    tot = 0
    for u in users:
        tot += GET_MIN(u.get_solution_time())
    print(f"Total time {tot} minutes")

def main():
    if args.db:
        novices, experts, _ = setup_redefinition()
    else:
        novices, experts = load_splitted_by_redefinition(os.path.join(dir_path, '../pickle/users_data.p'))

    

    if args.levels:
        # Plot Figure 4
        plot_levels(novices, experts, output_path = '/tmp/levels.pdf')

    if args.transitions:
        # Plot Figure 10
        plot_visited_bbs(novices, experts, output_path = '/tmp/visited_bbs.pdf')

    if args.two_sample_test:
        compute_2_sample_t_test(novices, experts)

    if args.sol_times:
        compute_average_solution_times(novices, experts)

    if args.groups:
        compute_average_solution_times_by_group(novices, experts)

    if args.threshold:
        get_threshold(novices + experts)
    
    if args.sum:
        cumulative(novices + experts)

if __name__ == '__main__':
    main()
