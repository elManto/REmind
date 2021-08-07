#!/usr/bin/env python

import os
import json
from base.config import config_dictionary, set_binary
from base.initialize import setup, setup_redefinition
from base.utils import generate_vectors
from base.pickle_loader import load, dump_p_values
from base.bb_classes import BB, UserViews, NodeType
import networkx
from enum import Enum
import angr
import argparse
import pickle




DESCR = """Basic Block analysis useful for Table 2, Figure 7, and discarded BBs"""

opt = argparse.ArgumentParser(description = DESCR)
opt.add_argument("--db", help = "Extracts data from the DB, default is the pickle", action='store_true', required=False)
opt.add_argument("--function_time", help = "Table 2, i.e., percentage function time", action='store_true', required = False)
opt.add_argument("--cfg", help = "Figure 7, i.e., Plot of cfg of chall 1", action = 'store_true', required = False)
opt.add_argument("--discarded_bbs", help = "Discarded BBs", action = 'store_true', required = False)
opt.add_argument("--pickle_dump", help = "Dumps out the BBs classes", action = 'store_true', required = False)
opt.add_argument("--statistics", help = "2-sample t-test about useless BBs for experts and novices (Fig 7)", action = 'store_true', required = False)

args = opt.parse_args()
dir_path = os.path.dirname(os.path.realpath(__file__))
PICKLE_P_VALUES = os.path.join(dir_path, '../pickle/p_values.p')

# Second binary data
binary_2 = {
'TARGET_NODE_NAME' : '<CFGNode checkIfSorted+0x97 [12]>',
'INTERESTING' : [0xd58, 0xcad, 0xb80, 0xbff, 0xb11, 0xa5f, 0x9e1, 0x937, 0x8ff],
'NON_INTERESTING' : [0xd18, 0xc4b, 0xacc, 0xa72, 0x89a],
'MAIN_ADDR' : hex(0xd58 + 0x400000),
'filename' : '../binaries/list',
'challenge_id' : 7
}

# First binary data
binary_1 = {
'TARGET_NODE_NAME' : '<CFGNode >',
'INTERESTING' : [0xb7a, 0xe04, 0xe5c],
'NON_INTERESTING' : [0xca4, 0xcb4, 0xce4],
'MAIN_ADDR' : hex(0xb7a + 0x400000),
'BRIDGE_ADDR' : hex(0xe5c + 0x400000),
'filename' : '../binaries/server',
'challenge_id' : 1
}

directory = os.path.dirname(__file__)
directory = os.path.expanduser(directory)
directory_path = os.path.abspath(directory)


GET_MIN = lambda a : (a / 60.0) / 1000.0
GET_ADDR = lambda a : a + ANGR_OFFSET
GET_FCN_NAME = lambda node : node.name.split("+")[0]
ANGR_OFFSET = 0x400000

total_bbs2time_1 = dict()
total_bbs2time_2 = dict()
MAX_TIME = 1000000 
MIN_TIME = 500


def initialize_total_dict():
    path_to_csv = os.path.join(directory_path, '../csv')
    assert(os.path.isdir(path_to_csv))
    with open(os.path.join(path_to_csv, './bbs_1.csv'), 'r') as bbs_1:
        bbs_1 = bbs_1.read().split(';')[:-1]
    with open(os.path.join(path_to_csv, './bbs_2.csv'), 'r') as bbs_2:
        bbs_2 = bbs_2.read().split(';')[:-1]
    for bb in bbs_1:
        total_bbs2time_1[bb] = []
    for bb in bbs_2:
        total_bbs2time_2[bb] = []
 

class BasicBlockAnalysis():

    def __init__(self, binary_info_dictionary):
        self.binary_dict = binary_info_dictionary
   
    
    def remove_entities(self, graph, entities):
        for entity in entities:
            if type(entity) is angr.knowledge_plugins.cfg.cfg_node.CFGNode:
                graph.remove_node(entity)
    
    
    def edit_graph(self, graph, func_offsets):
        offsets = [GET_ADDR(offset) for offset in func_offsets]
        nodes_to_remove = [node for node in graph.nodes if node.function_address not in offsets]
        self.remove_entities(graph, nodes_to_remove)
        return graph
    
    
    def find_target_node(self, graph, target_node_name):
        for node in graph.nodes:
            if str(node) == target_node_name:
                return node
    
    
    def find_node_by_name(self, graph, node_name):
        for node in graph.nodes:
            if str(node) == node_name:
                return node
    
    
    def find_node_by_addr(self, graph, addr):
        for node in graph.nodes:
            if hex(node.addr) == addr:
                return node
        return None


    def offsets(self):
        return self.binary_dict['INTERESTING'] + self.binary_dict['NON_INTERESTING']

    
    def get_bbs_2_time(self, bbs, deltas):
        res = dict()
    
        for bb, delta in zip(bbs, deltas):
            #if delta > 110000 or delta < 500: 
            if delta > MAX_TIME or delta < MIN_TIME:  
                continue
            if not bb in res:
                res[bb] = [delta]
            else:
                res[bb].append(delta)
        return res
    

    def generate_graph(self):
        challenge_id = self.binary_dict['challenge_id']
        filename = os.path.join(directory_path, self.binary_dict['filename'])
        assert(os.path.isfile(filename))
        MAIN_ADDR = self.binary_dict['MAIN_ADDR']
        target_node_name = self.binary_dict['TARGET_NODE_NAME']
        print(filename)
        p = angr.Project(filename, load_options={'auto_load_libs': False})
        cfg = p.analyses.CFG()
        graph = self.edit_graph(cfg.graph, self.offsets())
    
        target = self.find_target_node(graph, target_node_name)
        main = self.find_node_by_addr(graph, MAIN_ADDR)
        if challenge_id == 1:
            BRIDGE_ADDR = self.binary_dict['BRIDGE_ADDR']
            bridge = self.find_node_by_addr(graph, BRIDGE_ADDR)
        main2target = networkx.shortest_path_length(graph, main, target)
    
        return graph, main, target, main2target
    
    
    # The method where the actual analysis starts
    def analyse_task(self, users):
        challenge_id = self.binary_dict['challenge_id']
        graph, main, target, main2target = self.generate_graph()
        if challenge_id == 1:
            bridge_addr = self.binary_dict['BRIDGE_ADDR']
            bridge = self.find_node_by_addr(graph, bridge_addr)
        else:
            bridge = ''
    
        total_bbs2time = total_bbs2time_1 if challenge_id == 1 else total_bbs2time_2
        self.analyse_users(users, total_bbs2time, challenge_id)
        return self.analyse_bbs(total_bbs2time, graph, main, bridge, target, challenge_id)
    
    
    def analyse_users(self, users, total_bbs2time, challenge_id):
        # We extract the user_views for each user
        for user in users:
            events = user.chall[str(challenge_id)].raw_events
            if len(events) > 50:
                _, bbs, deltas = generate_vectors(events, False, True, challenge_id)    #TO CHECK
                bbs2time = self.get_bbs_2_time(bbs, deltas)
                for bb in total_bbs2time:
                    if bb in bbs2time:
                        user_view = UserViews(bbs2time[bb], user.redefinition, user.user_id)
                    else:
                        user_view = UserViews([0.0], user.redefinition, user.user_id)
                    total_bbs2time[bb].append(user_view)
    
    
    def analyse_bbs(self, total_bbs2time, graph, main, bridge, target, challenge_id):
        # For each BB we basically copy the corresponding user_views in the dedicated BB object
        # together with other info like distance, ...
        res = []
        for bb in total_bbs2time:
            node = self.find_node_by_addr(graph, bb)
            if node is not None:
                try:
                    length = networkx.shortest_path_length(graph, node, target)
                    if challenge_id == 1:
                        fcn_name = GET_FCN_NAME(node)
                        if fcn_name in ['sub_400ca4', 'sub_400cb4']:
                            distance = networkx.shortest_path_length(graph, main, node)
                        elif fcn_name in ['sub_400ce4']:
                            distance = networkx.shortest_path_length(graph, bridge, node)
                        else:
                            distance = 0
                    else:
                        distance = 0
    
                except networkx.exception.NetworkXNoPath:
                    fcn_name = GET_FCN_NAME(node)
                    if fcn_name in ['checkIfSorted']:
                        distance = 0
                    else:
                        distance = networkx.shortest_path_length(graph, main, node)
    
                if node.has_return:
                    type = NodeType.FOOTER
                elif not '+' in node.name:
                    type = NodeType.HEADER
                else:
                    type = NodeType.OTHER
    
                num_of_instructions = len(node.instruction_addrs)
                fcn_name = GET_FCN_NAME(node)
                times = total_bbs2time[bb]
    
                bb_obj = BB(node.addr, fcn_name, type, times, distance, num_of_instructions, challenge_id)
                res.append(bb_obj)
        return res


# this method implements the data of Table2
def fetch_statistics_time_per_function(bb_list, statistical_measure = 'avg'):
    import numpy as np
    statistical_fcn = np.average

    if statistical_measure == 'med':  
        statistical_fcn = np.median

    fcn_times_experts = {}
    fcn_times_novices = {}
    bb_per_function = {}
    tot_experts = 0
    tot_novices = 0
     
    for bb in bb_list:
        novices_times = [sum(user_view.times) for user_view in bb.user_views if not user_view.is_expert()]
        experts_times = [sum(user_view.times) for user_view in bb.user_views if user_view.is_expert()]
    
        stat_novice_per_bb = statistical_fcn(novices_times)
        stat_expert_per_bb = statistical_fcn(experts_times)

        tot_experts += stat_expert_per_bb
        tot_novices += stat_novice_per_bb

        fcn_name = bb.function

        if not fcn_name in fcn_times_experts:
            fcn_times_experts[fcn_name] = stat_expert_per_bb
            fcn_times_novices[fcn_name] = stat_novice_per_bb
            #bb_per_function[fcn_name] = 1
        else:
            fcn_times_experts[fcn_name] += stat_expert_per_bb
            fcn_times_novices[fcn_name] += stat_novice_per_bb
            #bb_per_function[fcn_name] += 1

    # Here we format the data and we compute the ratio
    print("Function\tExperts\tNovices\tRatio")
    for fcn in fcn_times_experts:
        perc_experts = round((fcn_times_experts[fcn] / float(tot_experts)) * 100, 2)
        perc_novices = round((fcn_times_novices[fcn] / float(tot_novices)) * 100, 2)
        ratio = round(fcn_times_novices[fcn] / fcn_times_experts[fcn], 2)

        print("`{0}`:  \t{1} ({2})\t{3} ({4})\t{5}".format(fcn, GET_MIN(fcn_times_experts[fcn]), perc_experts, GET_MIN(fcn_times_novices[fcn]), perc_novices, ratio))

    overall_ratio = round(tot_novices / float(tot_experts), 2)
    print("`Total`:  \t{0} (100%) \t{1} (100%) \t{2}".format(GET_MIN(tot_experts), GET_MIN(tot_novices), overall_ratio))


def cumulative_times_per_bbs(bbs_list):
    import numpy as np
    non_interesting_exp = {}
    non_interesting_nov = {}
    bbs_times_exp = {}
    bbs_times_nov = {}
    for bb in bbs_list:
        novices_times = [sum(user_view.times) for user_view in bb.user_views if not user_view.is_expert()]
        experts_times = [sum(user_view.times) for user_view in bb.user_views if user_view.is_expert()]
    
        avg_time_novice_per_bb = np.average(novices_times)
        avg_time_expert_per_bb = np.average(experts_times)
        
        bbs_times_nov[bb.get_offset()] = avg_time_novice_per_bb / 1000
        bbs_times_exp[bb.get_offset()] = avg_time_expert_per_bb / 1000

        distance = int(bb.distance)
        if distance > 0:
            non_interesting_nov[bb.get_offset()] = avg_time_novice_per_bb / 1000
            non_interesting_exp[bb.get_offset()] = avg_time_expert_per_bb / 1000
       
    return non_interesting_exp, non_interesting_nov, bbs_times_exp, bbs_times_nov

def build_useless_path_times(bbs_list):
    # similar to `cumulative_times_per_bbs` but instead, this method computes the time separated for each user, w.r.t. useless paths
    novices_times = []
    experts_times = []
    for bb in bbs_list:
        if int(bb.distance) > 0:
            tmp_novices_times = [sum(user_view.times) for user_view in bb.user_views if not user_view.is_expert()]
            tmp_experts_times = [sum(user_view.times) for user_view in bb.user_views if user_view.is_expert()]
            if not novices_times and not experts_times:
                novices_times = [t for t in tmp_novices_times]
                experts_times = [t for t in tmp_experts_times]
            else:
                for i in range(len(novices_times)):
                    novices_times[i] += tmp_novices_times[i]

                for i in range(len(experts_times)):
                    experts_times[i] += tmp_experts_times[i]
    return experts_times, novices_times
                     

def cfg_plot(bbs_list, input_file_name, output_path = '/tmp/cfg'):
    from cfg_plotter import GraphPlotter
    
    if not os.path.isdir(output_path):
        print("Generating output dir in {0} ".format(output_path))
        os.makedirs(output_path)
    non_interesting_exp, non_interesting_nov, bbs_times_exp, bbs_times_nov = cumulative_times_per_bbs(bbs_list)
    plotter = GraphPlotter(input_file_name, output_path)
    plotter.plot(non_interesting_exp, non_interesting_nov, bbs_times_exp, bbs_times_nov) 
    print("Plot generated succesfully in " + output_path)
    
        
def code_selection(list_of_bbs, num_of_experts = 33, num_of_novices = 39):
    tot_bbs_exp = [0 for i in range(0, num_of_experts)]
    tot_bbs_nov = [0 for i in range(0, num_of_novices)]
    discarded_bbs_experts = {}

    for bb in list_of_bbs:
        novices_times = [sum(user_view.times) for user_view in bb.user_views if not user_view.is_expert()]
        experts_times = [sum(user_view.times) for user_view in bb.user_views if user_view.is_expert()]
        addr = bb.address
        for i in range(0, num_of_experts):
            if experts_times[i] > 1.0:
                tot_bbs_exp[i] += 1
            #else:
            #    if bb in discarded_bbs_experts:
            #        discarded_bbs_experts[bb] += 1
            #    else:
            #        discarded_bbs_experts[bb] = 1

        for i in range(0, num_of_novices):
            if novices_times[i] > 1.0:
                tot_bbs_nov[i] += 1

    #t = float(len(list_of_bbs))
    #print("Experts")
    #for i in range(0, 20):
    #    perc = round(tot_bbs_exp[i] / t, 2)
    #    print(perc)

    #print("Novices")
    #for i in range(0, 32):
    #    perc = round(tot_bbs_nov[i] / t, 2)
    #    print(perc)
    import numpy as np
    print("Experts")
    #print(tot_bbs_exp)
    #print(np.average(tot_bbs_exp))
    #print(min(tot_bbs_exp))
    #print(max(tot_bbs_exp))
    tot_bbs_exp.append(131.0)
    print([(155 - bb) for bb in tot_bbs_exp])
    print(len(tot_bbs_exp))
    print(np.median(tot_bbs_exp))

    print("Novices")
    #print(tot_bbs_nov)
    #print(np.average(tot_bbs_nov[1:-2]))
    #print(min(tot_bbs_nov[1:-2]))
    #print(max(tot_bbs_nov[1:-2]))
    tot_bbs_nov.append(148)
    real_discarded = [(155 - bb) for bb in tot_bbs_nov]
    print(np.median(real_discarded))
    print(len(tot_bbs_nov))
    print(np.median(tot_bbs_nov))
       
def dump_bbs_to_pickle(list_of_bbs):
    with open(os.path.join(dir_path, '../pickle/basic_blocks.p'), 'wb') as f:
        pickle.dump(list_of_bbs, f)

def mean_confidence_interval(data, confidence=0.95):
    import numpy as np
    import scipy.stats
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h



def compute_2_sample_t_test(novices, experts):
    from scipy.stats import ttest_ind
    t, p = ttest_ind(novices, experts, equal_var=False)
    print("Confidence intervals computed with confidence == 0.95")
    conf_exp = mean_confidence_interval(experts)
    conf_nov = mean_confidence_interval(novices)
    print(f"Expert: {conf_exp}")
    print(f"Novice: {conf_nov}")
    print("\n2-sample t-test results")
    print(f"t: {t}")
    print(f"p-value: {p}")
    dump_p_values(PICKLE_P_VALUES, p)
 

def main():
    if args.db:
        novices, experts, all_users = setup_redefinition()
    else:
        #novices, experts = load_splitted_by_redefinition(os.path.join(dir_path, '../pickle/users_data.p'))
        all_users = load(os.path.join(dir_path, '../pickle/users_data.p'))

    initialize_total_dict()

    bb_analysis_1 = BasicBlockAnalysis(binary_1)
    bbs_list_1 = bb_analysis_1.analyse_task(all_users.all_users)

    bb_analysis_2 = BasicBlockAnalysis(binary_2)
    bbs_list_2 = bb_analysis_2.analyse_task(all_users.all_users)

    # On top of this, we can implement other specific analysis e.g., Table2, Figure7 and discarded BBs (i.e., data at the bottom of 6.2)

    if args.function_time:
        fetch_statistics_time_per_function(bbs_list_2, 'med')                 # Table2

    if args.cfg:
        filename = os.path.join(directory_path, binary_1['filename'])
        cfg_plot(bbs_list_1, filename)                                 # Figure7

    if args.discarded_bbs:
        code_selection(bbs_list_1 + bbs_list_2, 32, 38)                   # Discarded BBs

    if args.pickle_dump:
        dump_bbs_to_pickle(bbs_list_1 + bbs_list_2)

    if args.statistics:
        experts_useless_times, novices_useless_times = build_useless_path_times(bbs_list_1)

        experts_useless_times_7, novices_useless_times_7 = build_useless_path_times(bbs_list_2)
        print(f"Ratio useless time spent (Novices/Experts): {sum(novices_useless_times_7)/sum(experts_useless_times_7)}")

        compute_2_sample_t_test(novices_useless_times, experts_useless_times)   
        
        




if __name__ == '__main__':
    main()
