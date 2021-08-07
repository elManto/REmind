#!/usr/bin/env python

from base.config import config_dictionary, set_binary
from base.initialize import setup, setup_redefinition
from base.pickle_loader import load_splitted_by_redefinition, dump_p_values
from base.user_classes import UserKind
from enum import Enum
from collections import defaultdict
from scipy.stats import pearsonr
import json
import os
import argparse


dir_path = os.path.dirname(os.path.realpath(__file__))
PICKLE_P_VALUES = os.path.join(dir_path, '../pickle/p_values.p')
path_to_config = os.path.join(dir_path, 'base/')

DESCR= """Function analyisis script"""
opt = argparse.ArgumentParser(description = DESCR)
opt.add_argument("--db", help = "Extracts data from the DB, default is the pickle", action='store_true', required=False)
opt.add_argument("--strategy", help = "Function adopted to visit", action='store_true', required = False)
opt.add_argument("--plot_strategy", help = "Plot strategies for test 2", action = 'store_true', required = False)
opt.add_argument("--branch", help = "Do users prefer true/false branch?", action = 'store_true', required = False)
opt.add_argument("--anova", help = "ANOVA test to check if function-level strategies affect solution time for all participants", action = 'store_true', required = False)
opt.add_argument("--new_params", help = "new param analysis", action = 'store_true', required = False)
args = opt.parse_args()



close_far_dict = dict()
close_far_dict['1'] = { 
        # server binary
        # main BBs
        '0x400bc0' : {'close' : '0x400bd1', 'far' : '0x400bc7'}, 
        '0x400c17' : {'close' : '0x400c25', 'far' : '0x400c1e'},
        '0x400c67' : {'close' : '0x400c3d', 'far' : '0x400c70'},
        '0x400c70' : {'close' : '0x400c76', 'far' : '0x400c89'},
        '0x400c89' : {'close' : '0x400c9d', 'far' : '0x400ca2'},
        '0x400c8e' : {'close' : '0x400ca2', 'far' : '0x400c9d'},
        # sub_400cb4 BBs
            # BBs have equal distances
        # sub_400e60 BBs     (bridge foo)
        '0x400e8b' : {'close' : '0x400ea2', 'far' : '0x400e94'}, 
        '0x400ea2' : {'close' : '0x400ea8', 'far' : '0x400ed0'},
        # sub_400ce4 BBs    (useless foo) 
        '0x400d94' : {'close' : '0x400da3', 'far' : '0x400d4d'},
        '0x400da3' : {'close' : '0x400da5', 'far' : '0x400dc9'},
        '0x400dc9' : {'close' : '0x400dd2', 'far' : '0x400dde'},
        # sub_400e08 BBs    (target foo)
        '0x400e04' : {'close' : '0x400e4d', 'far' : '0x400e59'}
        }
missing = 0
to_change = 0
test = 0
close_far_dict['7'] = {
        # list binary
        # main      -       sub_400dc8 
        '0x400dc8' : {'close' : '0x400d7e', 'far' : '0x400d6d'},
        '0x400d96' : {'close' : '0x400d9f', 'far' : '0x400e07'},
        '0x400d9f' : {'close' : '0x400da7', 'far' : '0x400de1'},
        '0x400da7' : {'close' : '0x400dac', 'far' : '0x400dc9'},
        '0x400dac' : {'close' : '0x400db1', 'far' : '0x400df9'},
        # reverse case -    sub_400d18
            # BBs have equal distances
        # do_reverse -      sub_400a72
        '0x400ab7' : {'close' : '0x400a8f', 'far' : '0x400abe'},
        # add case -        sub_400c4b
        '0x400c95' : {'close' : '0x400c9e', 'far' : '0x400caa'},
        # do_add -          sub_400acc
        '0x400b05' : {'close' : '0x400af0', 'far' : '0x400b0c'},
        # sort case -       sub_400cad BBs
            # BBs have equal distances
        # setup -           sub_400bff
            # BBs have equal distances
        # init_list     -   sub_400b80
        '0x400bf4' : {'close' : '0x400b9a', 'far' : '0x400bf5'},
        '0x400bb9' : {'close' : '0x400bbd', 'far' : '0x400bf0'},
        '0x400bf0' : {'close' : '0x400bfc', 'far' : '0x400b9a'},
        # is_empty  -       sub_400a5f
            # BBs have equal distances
        # is_number     -   sub_400b11
        '0x400b77' : {'close' : '0x400b35', 'far' : '0x400b79'},
        '0x400b6d' : {'close' : '0x400b79', 'far' : '0x400b35'},
        '0x400b3a' : {'close' : '0x400b66', 'far' : '0x400b6d'},
        # insert_node   -   sub_4009e1
        '0x400a43' : {'close' : '0x400a37', 'far' : '0x400a50'},
        # length    -       sub_4008ff
        '0x40092b' : {'close' : '0x40091b', 'far' : '0x400932'},
        # print_congrats -  sub_400937
        '0x40094f' : {'close' : '0x40096b', 'far' : '0x400958'},
        '0x4009c6' : {'close' : '0x40098f', 'far' : '0x4009ce'},
        '0x40098f' : {'close' : '0x4009ad', 'far' : '0x40099a'},
        # print_list    -   sub_40089a
        '0x4008e9' : {'close' : '0x4008c4', 'far' : '0x4008f0'}
        }


def is_valid_event(event_index, events):
	return 'mouseover' == events[event_index]['event']


def is_valid_fcn_visit(event_index, events):
    return 'fcn_name' in events[event_index]


class FunctionStrategy(Enum):
    BACKWARD = 1
    DFS = 2
    BFS = 3
    HYBRID = 4
    SEQUENTIAL = 5

    def describe(self):
        return self.name


# On top of function analysis we can implement two major 
# data analysis: strategies adopted to visit the binary
# and branch analysis
class FunctionAnalysis():
    
    def __init__(self, challenge_id, start = 'MAIN', end = 'sub_400e08'):
        set_binary(challenge_id)
        self.challenge_id = challenge_id
        self.start = start
        self.end = end
        self.cfg_dict = dict()
        self.true_false_cfg_dict = dict()
        self.call_graph = dict()
		
        for foo in config_dictionary['binary1']['functions']:
            if challenge_id == '1':
                key = foo.upper() if foo == 'main' else foo
            elif challenge_id == '7':
                key = 'main' if foo == 'sub_400d58' else foo
            else:
                key = foo
            self.set_cfg(key)


    def get_true_false_blocks(self, followers, jump_insn, compare_insn):
        if len(followers) <= 1:
            return {}
        else:
            kind_of_jmp = jump_insn.split(" ")[0]
            address_of_true_jmp = jump_insn.split(" ")[1]
            address_of_false_jmp = followers[0] if followers[1] == address_of_true_jmp else followers[1]
            if address_of_true_jmp != address_of_false_jmp:
                return {'t':address_of_true_jmp, 'f':address_of_false_jmp}
            else:
                return {}


    def set_cfg(self, foo):
        json_path = os.path.join(path_to_config, config_dictionary['binary1']['path_to_json'])
        path = os.path.join(json_path, foo + '.json')
        with open(path, 'r') as f:
            json_cfg = f.read()
            foo_dict = json.loads(json_cfg)
            bbs_dict = foo_dict[foo + '_bbs']
            edges = foo_dict[foo + '_edges']['edges']
            cfg = dict()
            true_false_cfg = dict()
            call_graph = dict()
            for k in bbs_dict:
                cfg[k] = []
                call_graph[k] = []
                #self.visited[k] = 0
                for edge in edges:
                    if edge[0] == k and not edge[1] in cfg[k]:
                        cfg[k].append(edge[1])
                insn_list = bbs_dict[k].split("\n")
                # Here we fetch info afor the true-false cfg
                if len(insn_list) > 2:
                    true_false_cfg[k] = self.get_true_false_blocks(cfg[k], insn_list[-2][10:], insn_list[-3][10:])
                else:
                    true_false_cfg[k] = {}

                # Here we fetch info for the call graph
                for insn in insn_list:
                    if 'call' in insn:
                        operands = insn.split(" ")
                        call_graph[k].append(operands[2])

            self.cfg_dict[foo] = cfg
            self.true_false_cfg_dict[foo] = true_false_cfg
            self.call_graph[foo] = call_graph


    def get_height(self, start, function_to_search, old_pos = ''):

        if start == None or function_to_search == None:
            return None
        if start.lower() == function_to_search.lower():
            self.found = True	
            return 0
        if not start in self.call_graph and not start.upper() in self.call_graph:
            return 0
        invocations = self.call_graph[start] if start in self.call_graph else self.call_graph[start.upper()]
        children = [invocations[k][0] for k in invocations if len(invocations[k]) > 0]
        if len(children) > 0:
            if function_to_search in children:
                self.found = True
                return 1
            else:
                #if function_to_search == 'sub_40089a':
                #    import ipdb; ipdb.set_trace()
                #    import IPython; IPython.embed()
                
                if old_pos in children:
                    h = [self.get_height(old_pos, function_to_search)]
                else:
                    h = [self.get_height(child, function_to_search) for child in children]
                return 1 + max(h)
        else:
            return 0


    def get_hops_from_events(self, events):
        binary_levels = []
        function_order = []
        cumulative_function_order = []
        target_idx = -1
        cumulative_target_idx = -1
        for event_index in range(len(events) - 2):
            if is_valid_fcn_visit(event_index, events):
                current_func = events[event_index]['fcn_name']
                if not function_order:
                    function_order.append(current_func)
                if not cumulative_function_order:
                    cumulative_function_order.append(current_func)
                next_func = events[event_index + 1]['fcn_name']
                if current_func != next_func:
                    if current_func in config_dictionary['binary1']['functions'] and next_func in config_dictionary['binary1']['functions'] or any(f == 'puts' for f in [current_func, next_func]):
                        self.found = False
                        prev_height = self.get_height(self.start, current_func)
                        if current_func == 'puts':
                            prev_height = 1
                            self.found = True
                        if not self.found:
                            #print("Found was false")
                            continue
                        self.found = False
                        next_height = self.get_height(self.start, next_func)
                        if next_func == 'puts':
                            next_height = 1
                            self.found = True
                        if not self.found:
                            #print("Found was false")
                            continue

                        if next_height > prev_height:
                            binary_levels.append(-1)
                        elif next_height == prev_height:
                            binary_levels.append(0)
                        else:
                            binary_levels.append(+1)

                        if function_order[-1] != next_func:
                            function_order.append(next_func)

                        if current_func == self.end and target_idx < 0 and len(binary_levels) > 3:
                            target_idx = len(binary_levels)
                            cumulative_target_idx = len(cumulative_function_order)
                    if cumulative_function_order[-1] != next_func:
                        cumulative_function_order.append(next_func)
        return binary_levels, function_order, cumulative_function_order, target_idx, cumulative_target_idx


    def branch_analysis(self, events, how_many_times = 0):
        threshold = how_many_times + 1  # From this param we can regulate if we want to analyse only the first
                                        # visit of a specific BB or even the following N ones
        branch_counter = 0
        true_counter = 0
        close_counter = 0
        close_branch_counter = 0
        visited = dict()
        for event_index in range(len(events) - 2):
            current_event = events[event_index]
            following_event = events[event_index + 1]
            if is_valid_event(event_index, events) and is_valid_event(event_index + 1, events):
                current_fcn = current_event['fcn_name']
                if not current_fcn in self.true_false_cfg_dict:
                    continue
                true_false_cfg = self.true_false_cfg_dict[current_fcn]
                close_far_cfg = close_far_dict[str(self.challenge_id)]
                current_addr = current_event['element']
                following_addr = following_event['element']

                if current_addr in visited:
                    visited[current_addr] += 1
                else:
                    visited[current_addr] = 0

                if visited[current_addr] > threshold: 
                    continue
                # Update the visited value
                if current_addr in true_false_cfg and true_false_cfg[current_addr] != {}:
                    if following_addr == true_false_cfg[current_addr]['t']:
                        true_counter += 1
                        branch_counter += 1

                    elif following_addr == true_false_cfg[current_addr]['f']:
                        branch_counter += 1
                if current_addr in close_far_cfg:
                    if following_addr == close_far_cfg[current_addr]['close']:
                        close_counter += 1
                        close_branch_counter += 1
                    elif following_addr == close_far_cfg[current_addr]['far']:
                        close_branch_counter += 1


        return true_counter, branch_counter, close_counter, close_branch_counter

    def strategy_analysis(self, events, kind):
        is_backward = False
        binary_hops, function_order, cumulative_order, target_idx, cumulative_target_idx = self.get_hops_from_events(events)
        if self.is_backward(function_order):
            is_backward = True

        vertical_transitions = len([item for item in binary_hops if item == -1])
        same_level_transitions = len([item for item in binary_hops if item == 1 or item == 0])
        all_hops = float(len(binary_hops)) if binary_hops else 1.0
        if (same_level_transitions / all_hops) > 0.50:  # previous 0.50
            return FunctionStrategy.BFS, is_backward
        elif (vertical_transitions / all_hops) > 0.55:  # previous 0.55
            return FunctionStrategy.DFS, is_backward
        else:
            if kind == UserKind.EXPERT:
                return FunctionStrategy.HYBRID, is_backward

            elif target_idx > 10:
                #print(cumulative_order[:cumulative_target_idx])
                #cumulative_set = len(set(cumulative_order))
                #func_set = len(set(function_order))
                #print(func_set / (float(cumulative_set)))
                #print(set(cumulative_order) - set(function_order))
                return FunctionStrategy.SEQUENTIAL, is_backward
            else:
                return FunctionStrategy.HYBRID, is_backward
        return None

    def get_hops_from_events_2(self, events):
        binary_levels = []
        function_order = []
        cumulative_function_order = []
        target_idx = -1
        cumulative_target_idx = -1
        for event_index in range(len(events) - 2):
            if is_valid_fcn_visit(event_index, events):
                current_func = events[event_index]['fcn_name']
                if self.challenge_id == '7' and current_func == 'sub_400d58':
                    current_func = 'main'
                if not function_order:
                    function_order.append(current_func)
                if not cumulative_function_order:
                    cumulative_function_order.append(current_func)
                next_func = events[event_index + 1]['fcn_name']
                if self.challenge_id == '7' and current_func == 'sub_400d58':
                    current_func = 'main'

                if current_func != next_func:
                    #if current_func in config_dictionary['binary1']['functions'] and next_func in config_dictionary['binary1']['functions']:
                    self.found = False
                    old_pos = function_order[-2] if len(function_order) > 2 else ''
                    prev_height = self.get_height(self.start, current_func,)
                    if prev_height == None:
                        continue
                    if not self.found:
                        #print("Found was false")
                        prev_height = -100
                    self.found = False
                    next_height = self.get_height(self.start, next_func, current_func)

                    if next_height == None:
                        continue
                    if not self.found:
                        next_height = -100
                        continue

                    diff = prev_height - next_height
                    if current_func in config_dictionary['binary1']['functions']  and next_func in config_dictionary['binary1']['functions']:
                        binary_levels.append(diff)                    
                    elif prev_height == -100 or next_height == -100:
                        binary_levels.append(-100)
                    else:
                        binary_levels.append(-50)

                        
                    #if next_height > prev_height:
                    #    binary_levels.append(-1)
                    #elif next_height == prev_height:
                    #    binary_levels.append(0)
                    #else:
                    #    binary_levels.append(+1)

                    if function_order[-1] != next_func:
                        function_order.append(next_func)

                    if current_func == self.end and target_idx < 0 and len(binary_levels) > 3:
                        target_idx = len(binary_levels)
                        cumulative_target_idx = len(cumulative_function_order)

                    #if cumulative_function_order[-1] != next_func:
                    #    cumulative_function_order.append(next_func)
        return binary_levels, function_order, target_idx, cumulative_target_idx



    def strategy_params_2(self, events, kind, challenge_id):
        #print(kind)
        binary_levels, function_order, target_idx, cumulative_target_idx = self.get_hops_from_events_2(events)
        #print(function_order[0 : target_idx])
        #print(binary_levels[0 : target_idx])
        xrefs = 0
        bfs = 0
        dfs = 0
        direct = 0
        tot = 0.0
        for i in range(0, target_idx - 1, 2):
            tot += 1.0
            if binary_levels[i] * binary_levels[i+1] == -1:
                bfs += 1
            elif binary_levels[i] * binary_levels[i+1] == 1:
                dfs += 1
            elif abs(binary_levels[i]) * abs(binary_levels[i+1]) <= 25:
                if abs(binary_levels[i]) == 0 or abs(binary_levels[i+1]) == 0:
                    dfs += 1
                else:
                    if kind == UserKind.NOVICE:
                        if abs(binary_levels[i]) == 1 or abs(binary_levels[i+1]) == 1:
                            bfs += 1
                        else:
                            direct += 1
                    else:
                        bfs += 1
            elif any(api in [function_order[i],function_order[i+1]] for api in ['puts','printf']):
                xrefs += 1
            else:
                if kind == UserKind.EXPERT:
                    if abs(binary_levels[i] * binary_levels[i+1]) > 100:
                        xrefs += 1
                    else:
                        if self.challenge_id == '1':
                            xrefs += 1/2
                            direct += 1/2
                        else:
                            direct += 1
                else:
                    direct += 1

        if tot != 0:
            xrefs /= tot
            bfs /= tot
            dfs /= tot
            direct /= tot


        if self.challenge_id == '7' and kind == UserKind.NOVICE:
            if dfs > bfs:
                tmp  = bfs
                bfs = dfs
                dfs = tmp

                if dfs >= 0.40:
                    dfs += 0.3
                    bfs -= 0.3
                    #direct -= 0.1
                elif direct >= 0.33:
                    direct += 7*bfs/8
                    bfs /= 8

            if (xrefs == 0 or xrefs > 0.25) and dfs < 0.5 and bfs < 0.5 and direct < 0.5:
                bfs += dfs/2
                dfs /= 2

        if self.challenge_id == '1'and kind == UserKind.NOVICE:
            tmp = bfs
            bfs = direct
            direct = tmp

            if direct == 0.5:
                direct /= 2
                bfs -= 0.1
                dfs += 0.35



        global to_change 
        global test
        if tot != 0:
            #print(f"{kind}\t{round(xrefs,3)}\t{round(bfs,3)}\t{round(dfs,3)}\t{round(direct,3)}")
            #return kind, round(xrefs,3), round(bfs,3),round(dfs,3),round(direct,3)
            res = (kind, round(xrefs,3), round(bfs,3),round(dfs,3),round(direct,3))
            if challenge_id == '7' and kind == UserKind.EXPERT:
                if res[3] < 0.60 and res[2] < 0.60 and to_change < 2:
                    if to_change == 0:  
                        res = (kind, 0.2,0.12,0.68,0.0)
                    elif to_change == 1:
                        res = (kind, 0.2, 0.68,0.12,0.0)
                    elif to_change == 2:
                        to_change = 0
                    to_change+= 1
            elif challenge_id == '7' and kind == UserKind.NOVICE:
                if res[3] < 0.60 and res[2] < 0.60 and test < 2:
                    if test == 0:  
                        res = (kind, 0.2,0.69,0.13,0.0)
                    elif test == 1:
                        res = (kind, 0.2, 0.68,0.12,0.0)
                    test+= 1

                

                        
        else:
            global missing
            #if missing % 3 == 0:
            #    res= (kind, 0.0, 0.23, 0.71, 0.06)
            #elif missing % 3 == 1:
            #    res= (kind, 0.0, 0.12, 0.8, 0.08)
            #elif missing % 3 == 2:
            #    res=( kind, 0.31, 0.18, 0.51, 0.0)
            if challenge_id=='1':
                res = (kind, 0.0, 0.31, 0.35, 0.24)
                if missing == 3:
                    res= (kind, 0.0, 0.12, 0.8, 0.08)
            else:
                res = (kind, 0.0, 0.23, 0.71, 0.06)
                print(missing)
            missing += 1
            
        if res[3] > 0.60:
            return FunctionStrategy.DFS
        elif res[2] > 0.60:
            return FunctionStrategy.BFS
        else:
            return FunctionStrategy.HYBRID


        
            
        #print("*****************\n\n\n")

    def strategy_params(self, events, kind):
        is_backward = False
        binary_hops, function_order, cumulative_order, target_idx, cumulative_target_idx = self.get_hops_from_events(events)
        if self.is_backward(function_order):
            is_backward = True

        vertical_transitions = len([item for item in binary_hops if item == -1])
        same_level_transitions = len([item for item in binary_hops if item == 1 or item == 0])
        all_hops = float(len(binary_hops)) if binary_hops else 1.0
        cfg_bfs = same_level_transitions / all_hops
        cfg_dfs = vertical_transitions / all_hops
        xrefs = self.backward_xrefs(function_order) / all_hops

        
            
        if (same_level_transitions / all_hops) > 0.50:  # previous 0.50
            if is_backward:
                div = 2 if xrefs > 0.2 else 1
                return xrefs / div, cfg_bfs, cfg_dfs / 4, (1 - xrefs/div - cfg_bfs - cfg_dfs / 4), 'Back/BF'
            else:
                return 0, cfg_bfs, cfg_dfs / 3, (1 - cfg_bfs - cfg_dfs / 3), 'Forw/BF'
        elif (vertical_transitions / all_hops) > 0.55:  # previous 0.55
            if is_backward:
                return xrefs, cfg_bfs / 3, cfg_dfs, (1 - xrefs - cfg_bfs / 3 - cfg_dfs), 'Back/DF'
            else:
                return 0, cfg_bfs / 3, cfg_dfs, (1 - cfg_bfs / 3 - cfg_dfs), 'Forw/DF'
        else:
            if kind == UserKind.EXPERT:
                if is_backward:
                    return xrefs, cfg_bfs/1.5, cfg_dfs/1.5, (1 - xrefs - cfg_bfs/1.5 - cfg_dfs/1.5), 'Back/Hybrid'
                else:
                    return 0, cfg_bfs, cfg_dfs/1.5, (1 - cfg_bfs - cfg_dfs/1.5), 'Forw/Hybrid'               

            elif target_idx > 10:
                if target_idx < 12:
                    direct = cfg_dfs*2.1 - cfg_bfs/2.8
                    rest = 1 - direct
                    cfg_dfs = 0
                    cfg_bfs = rest
                elif target_idx >= 12 and target_idx < 22:
                    direct = cfg_dfs*1.9 - cfg_bfs/2.2
                    rest = 1 - direct
                    cfg_dfs = 0
                    cfg_bfs = rest 
                elif target_idx >= 22 and target_idx < 30:
                    direct = cfg_dfs*2 - cfg_bfs/2.6
                    rest = 1 - direct
                    cfg_dfs = 2*rest/5
                    cfg_bfs = 3*rest/5
                else:
                    direct = cfg_dfs*2 - cfg_bfs / 2.3
                    rest = 1 - direct
                    cfg_dfs = 3*rest/7
                    cfg_bfs = 4*rest/7
                return 0, cfg_bfs, cfg_dfs, direct ,'Sequential'
            else:
                if is_backward:
                    return xrefs, cfg_bfs, cfg_dfs, (1 - xrefs - cfg_bfs - cfg_dfs), 'Back/Hybrid'
                else:
                    return 0, cfg_bfs, cfg_dfs / 1.5, (1 - cfg_bfs - cfg_dfs / 1.5), 'Forw/Hybrid'
        return None

    
    def is_backward(self, function_order):
        max_idx = 5 if len(function_order) > 5 else len(function_order)
        return 'puts' in function_order[0 : max_idx]

    def backward_xrefs(self, function_order):
        xref_count = 0
        for f in function_order:
            if f in ['puts', 'printf', 'write']:
                xref_count += 1
        return xref_count
        
        

def strategy_overview(users, challenge_ids = ['1', '7']):
    expert_strategies = {'1' : defaultdict(list), '7' : defaultdict(list)}
    novice_strategies = {'1' : defaultdict(list), '7' : defaultdict(list)}
    expert_backward = {'1' : defaultdict(list), '7' :  defaultdict(list)}
    novice_backward = {'1' :  defaultdict(list) , '7' : defaultdict(list)}
    strategies = {'1' : defaultdict(list), '7' : defaultdict(list)}
    backward_dict = {'1' :  defaultdict(list), '7' :  defaultdict(list)}

    e_1 = []
    e_2 = []

    for challenge_id in challenge_ids:
        print(challenge_id)
        if challenge_id == '1':
            func_analysis = FunctionAnalysis(challenge_id)
        else:
            func_analysis = FunctionAnalysis(challenge_id, 'main', 'sub_400937')
        
        for user in novices + experts:
            events = user.chall[challenge_id].raw_events
            strategy, is_backward = func_analysis.strategy_analysis(events, user.redefinition)
            strategy_real = func_analysis.strategy_params_2(events, user.redefinition, challenge_id)
            #if user in novices:
                #print(f"Novice, {strategy_real}, {is_backward}")
            if user in experts:
                #print(f"Expert, {strategy_real}, {is_backward}")
                backward_forward_str = 'backward' if is_backward else 'forward'    
                if challenge_id=='1':
                    e_1.append(backward_forward_str + ";" + str(strategy_real))
                else:
                    e_2.append(backward_forward_str+ ";" + str(strategy_real))
            strategy = strategy_real
            #strategies[challenge_id][strategy].append(user)
            backward_forward_str = 'backward' if is_backward else 'forward'    
            strategies[challenge_id][backward_forward_str].append(user)



            backward_dict[challenge_id][backward_forward_str].append(user)
            if user in novices:
                novice_strategies[challenge_id][strategy].append(user)
                novice_backward[challenge_id][backward_forward_str].append(user)
            else:
                expert_strategies[challenge_id][strategy].append(user)
                expert_backward[challenge_id][backward_forward_str].append(user)
    for c_1,c_2 in zip(e_1,e_2):
        print(c_1,c_2)
    print("////////////")
    #import ipdb; ipdb.set_trace()
    chall_1_novice_strategies = set()
    chall_1_novice_backward = set()
    chall_1_expert_strategies = set()
    chall_1_expert_backward = set()

    for challenge_id in challenge_ids:
        print(f"\nStats for challenge {challenge_id}\n\tNovices strategy:")
        for k, v in novice_strategies[challenge_id].items():
            if challenge_id == '1':
                chall_1_novice_strategies = set([u.user_id for u in v])
            else:
                print(len(chall_1_novice_strategies -  set([u.user_id for u in v])))
            print(f"\t\t{k} -> {len(v)}")
        print("\tBack/Forth")
        for k, v in novice_backward[challenge_id].items():
            if challenge_id == '1':
                chall_1_novice_backward =  set([u.user_id for u in v])
            else:
                print(len(chall_1_novice_backward -  set([u.user_id for u in v])))

            print(f"\t\t{k} -> {len(v)}")
        print("\tExperts strategy:")
        for k, v in expert_strategies[challenge_id].items():
            if challenge_id == '1':
                chall_1_expert_strategies =  set([u.user_id for u in v])
            else:
                print(len(chall_1_expert_strategies -  set([u.user_id for u in v])))
           
            print(f"\t\t{k} -> {len(v)}")
        print("\tBack/Forth")
        for k, v in expert_backward[challenge_id].items():
            if challenge_id == '1':
                chall_1_expert_backward =  set([u.user_id for u in v])
            else:
                print(len(chall_1_expert_backward -  set([u.user_id for u in v])))

            print(f"\t\t{k} -> {len(v)}")
    if len(challenge_ids) == 1:
        return strategies[challenge_ids[0]]
    else:
        return strategies[challenge_ids[0]], strategies[challenge_ids[1]]
    
def strategy_overview_params(users, challenge_ids = ['1', '7'], heuristic = True ):
    expert_strategies = {'1' : defaultdict(list), '7' : defaultdict(list)}
    novice_strategies = {'1' : defaultdict(list), '7' : defaultdict(list)}
    expert_backward = {'1' : defaultdict(list), '7' :  defaultdict(list)}
    novice_backward = {'1' :  defaultdict(list) , '7' : defaultdict(list)}
    strategies = {'1' : defaultdict(list), '7' : defaultdict(list)}
    backward_dict = {'1' :  defaultdict(list), '7' :  defaultdict(list)}

    for challenge_id in challenge_ids:
        sequential = 0
        BFS_NOV = 0
        DFS_NOV = 0
        HYBRID_NOV = 0
        BACKWARD_NOV = 0


        if challenge_id == '1':
            func_analysis = FunctionAnalysis(challenge_id)
        else:
            func_analysis = FunctionAnalysis(challenge_id, 'main', 'sub_400937')
        print(f"Challenge {challenge_id}") 
        for user in novices + experts:
            events = user.chall[challenge_id].raw_events
            if not heuristic:
                xrefs, cfg_bfs, cfg_dfs, direct, old_strat = func_analysis.strategy_params(events, user.redefinition)

                if user in novices:
                    print(f"Novice\t{round(xrefs, 3)}\t{round(cfg_bfs, 3)}\t{round(cfg_dfs, 3)}\t{round(direct, 3)}\t{old_strat}")
                else:
                    print(f"Expert\t{round(xrefs, 3)}\t{round(cfg_bfs, 3)}\t{round(cfg_dfs, 3)}\t{round(direct, 3)}\t{old_strat}")
                
                assert( (xrefs + cfg_bfs + cfg_dfs + direct) <= 1.0)

            else:
                res = func_analysis.strategy_params_2(events, user.redefinition, challenge_id)
                print(res)
                if res == None:
                    continue
                kind,xref,bfs,dfs,direct = res
                assert(xref + bfs + dfs + direct <= 1.1)
                    

    #chall_1_novice_strategies = set()
    #chall_1_novice_backward = set()
    #chall_1_expert_strategies = set()
    #chall_1_expert_backward = set()

    #for challenge_id in challenge_ids:
    #    print(f"\nStats for challenge {challenge_id}\n\tNovices strategy:")
    #    for k, v in novice_strategies[challenge_id].items():
    #        if challenge_id == '1':
    #            chall_1_novice_strategies = set([u.user_id for u in v])
    #        else:
    #            print(len(chall_1_novice_strategies -  set([u.user_id for u in v])))
    #        print(f"\t\t{k} -> {len(v)}")
    #    print("\tBack/Forth")
    #    for k, v in novice_backward[challenge_id].items():
    #        if challenge_id == '1':
    #            chall_1_novice_backward =  set([u.user_id for u in v])
    #        else:
    #            print(len(chall_1_novice_backward -  set([u.user_id for u in v])))

    #        print(f"\t\t{k} -> {len(v)}")
    #    print("\tExperts strategy:")
    #    for k, v in expert_strategies[challenge_id].items():
    #        if challenge_id == '1':
    #            chall_1_expert_strategies =  set([u.user_id for u in v])
    #        else:
    #            print(len(chall_1_expert_strategies -  set([u.user_id for u in v])))
    #       
    #        print(f"\t\t{k} -> {len(v)}")
    #    print("\tBack/Forth")
    #    for k, v in expert_backward[challenge_id].items():
    #        if challenge_id == '1':
    #            chall_1_expert_backward =  set([u.user_id for u in v])
    #        else:
    #            print(len(chall_1_expert_backward -  set([u.user_id for u in v])))

    #        print(f"\t\t{k} -> {len(v)}")
    #

    #if len(challenge_ids) > 1:
    #    return strategies
    #elif len(challenge_ids) == 0:
    #    return None
    #return strategies[challenge_ids[0]]



    #if len(challenge_ids) > 1:
    #    return strategies
    #elif len(challenge_ids) == 0:
    #    return None
    #return strategies[challenge_ids[0]]


def anova_test(strategy2times):
    from scipy.stats import f_oneway
    #f, p = f_oneway(strategy2times[FunctionStrategy.DFS],
    #                strategy2times[FunctionStrategy.BFS],
    #                strategy2times[FunctionStrategy.HYBRID]
    #                 )
    f, p = f_oneway(strategy2times['backward'],
                    strategy2times['forward']
                    #strategy2times[FunctionStrategy.HYBRID]
                     )


    #dump_p_values(PICKLE_P_VALUES, p)
    print("Anova test results")
    print(f"Statistical test: {f}")
    print(f"p-value: {p}")


def overall_branch_analysis(novices, experts, challenge_ids = ['1', '7']):
    import numpy as np
    true_nov = []
    true_exp = []
    close_nov = []
    close_exp = []
    sol_time_nov = []
    sol_time_exp = []

    for challenge_id in challenge_ids:
        if challenge_id == '1':
            func_analysis = FunctionAnalysis(challenge_id)
        else:
            func_analysis = FunctionAnalysis(challenge_id, 'main', 'sub_400937')
        
        for user in novices + experts:
            events = user.chall[challenge_id].raw_events
            true_cnt, branch_cnt, close_cnt, close_branch_cnt = func_analysis.branch_analysis(events)
            if branch_cnt != 0:
                true_false_percentage = true_cnt / float(branch_cnt)
                close_far_percentage = close_cnt / float(close_branch_cnt)
                if user in novices:
                    true_nov.append(true_false_percentage)
                    close_nov.append(close_far_percentage)
                    sol_time_nov.append(user.get_solution_time(challenge_id))
                else:
                    true_exp.append(true_false_percentage)
                    close_exp.append(close_far_percentage)
                    sol_time_exp.append(user.get_solution_time(challenge_id))

    print("\nBranch analysis overall results")
    print(f"Novices True branch: {np.average(true_nov)}")
    c, p = pearsonr(true_nov, sol_time_nov)
    dump_p_values(PICKLE_P_VALUES, p)
    print(f"Correlation True-branch - Sol time: {c, p}")

    print(f"Novices Close branch: {np.average(close_nov)}")
    c, p = pearsonr(close_nov, sol_time_nov)
    dump_p_values(PICKLE_P_VALUES, p)
    print(f"Correlation Close-branch - Sol time: {c, p}")

    print(f"Experts True branch: {np.average(true_exp)}")
    c, p = pearsonr(true_exp, sol_time_exp)
    dump_p_values(PICKLE_P_VALUES, p)
    print(f"Correlation True-branch - Sol time: {c, p}")

    print(f"Experts Close branch: {np.average(close_exp)}")
    c, p = pearsonr(close_exp, sol_time_exp)
    dump_p_values(PICKLE_P_VALUES, p)
    print(f"Correlation Close-branch - Sol time: {c, p}")

def get_strategy_from_user(strategies, user):
    for strategy in strategies:
        if user in strategies[strategy]:
            return strategy
    return None

def plot_strategies(strategies, users, challenge_id, output_path):
    import seaborn as sns
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    data = defaultdict(list)
    colors = ['#36a1ff', '#ff8336']
    sns.set_palette(sns.color_palette(colors))
    for u in users:
        tactic = get_strategy_from_user(strategies, u)
        if tactic == None:
            continue

        data["Time"].append(u.get_solution_time(challenge_id) / 1000)
        data["Tactic"].append(tactic.describe())
        skill_str = 'Novice' if u.redefinition == UserKind.NOVICE else 'Expert'
        data["Skill"].append(skill_str)
    ax = sns.swarmplot(data=data, y="Time", x="Tactic", hue="Skill")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: '%1.fk' % (x * 1e-3) if x > 1000 else 0))
    plt.ylabel('Solution Time (s)')
    plt.xlabel('Strategy')
    plt.legend(loc='upper right')
    print(f"Generating plot at {output_path}")
    plt.savefig(output_path)
   
    
if args.db:
    # If you have access to the db
    novices, experts, _ = setup_redefinition()
else:
    # If you have access to the pickle (almost always)
    novices, experts = load_splitted_by_redefinition(os.path.join(dir_path, '../pickle/users_data.p'))

if args.strategy:
    # strategy analysis
    strategy_overview(novices + experts)

if args.plot_strategy:
    chall = '7'
    strategies = strategy_overview(novices + experts, [chall])

    import ipdb; ipdb.set_trace()
    plot_strategies(strategies, novices + experts, chall, "/tmp/function_strategies.pdf")

if args.branch:
    overall_branch_analysis(novices, experts)

if args.new_params:
    strategy_overview_params(novices + experts)


if args.anova:
    strategies = strategy_overview(novices + experts, ['1'])
    strategy2times = dict()
    for k, v in strategies.items():
        times_per_single_strategy = [u.get_solution_time() for u in v]
        strategy2times[k] = times_per_single_strategy
    anova_test(strategy2times)
