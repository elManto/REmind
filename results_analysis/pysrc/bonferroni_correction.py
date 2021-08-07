#!/usr/bin/env python

from base.pickle_loader import load_splitted_by_redefinition, dump_p_values, load_p_values
from base.p_values import Pvalues
from base.initialize import setup_redefinition, reputation_heuristic
from statsmodels.sandbox.stats.multicomp import multipletests
import argparse
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
PICKLE_P_VALUES = os.path.join(dir_path, '../pickle/p_values.p')


GET_MIN = lambda a : (a / 60.0) / 1000.0

DESCR = """Applies Bonferroni method to a set of p-values for all the statistical data"""
opt = argparse.ArgumentParser(description = DESCR)
opt.add_argument("--db", help = "Extract data directly from db, if not set it uses the pickle", action = 'store_true', required = False)
args = opt.parse_args()               

def bonferroni():
    p_values = load_p_values(PICKLE_P_VALUES)
    print(p_values)
    p_adjusted = multipletests(p_values, method = 'bonferroni')
    print(f"\n\n{p_adjusted}")
    
    
    

def main():
    if args.db:
        novices, experts, _ = setup_redefinition()
    else:
        novices, experts = load_splitted_by_redefinition(os.path.join(dir_path, '../pickle/users_data.p'))

    bonferroni()

if __name__ == '__main__':
    main()
