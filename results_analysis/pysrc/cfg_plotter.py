import os
import angr
import pygraphviz as pgv

LABEL = 20
ANGR_OFFSET = 0x400000
INTERESTING = [0xb7a, 0xe08, 0xe60]
NON_INTERESTING = [0xca4, 0xcb4, 0xce4]
MAX_TIME_USELESS_STUFF = 168.0
MAX_TIME_USEFUL_STUFF = 547
OFFSETS = INTERESTING + NON_INTERESTING

GET_RGB = lambda a : hex(255 - (int((255 * a) / MAX_TIME_USELESS_STUFF)))
GET_RGB_FROM_PERCENTAGE = lambda a : hex(255 - 6 * int(255 * a))
GET_RGB_INTERESTING = lambda a : hex(255 - (int((255 * a) / MAX_TIME_USEFUL_STUFF)))
GET_ADDR = lambda a : a + ANGR_OFFSET
GET_OFFSET = lambda a : hex(a - ANGR_OFFSET)
COLORS = ['white', 'yellow', 'red', 'blue', 'black']

NON_INTERESTING_NOVICES = '0xd31,0xcb4,0xd5c,0xcc5,0xd4b,0xd4d,0xda3,0xdd2,0xcd6,0xce4,0xdde,0xca4,0xded,0xd94,0xdc9,0xdac,0xd76,0xdc7,0xcdd,0xdb8'
NON_INTERESTING_EXPERTS = '0xd31,0xd5c,0xcc5,0xd94,0xcb4,0xd76,0xca4,0xce4,0xcdd,0xdb8'

TOTAL_EXPERTS = '0xe5c,0xd31,0xe04,0xd5c,0xc67,0xc3d,0xe4d,0xbd1,0xea0,0xbf0,0xb7a,0xc17,0xea2,0xca4,0xc34,0xc25,0xd76,0xc52,0xe79,0xea8,0xce4,0x910,0x922,0x920,0xcc5,0xec1,0xe8b,0xc0a,0xed0,0xbc0,0xcb4,0xbb3,0xd94,0xbe3,0xc1e,0xdb8,0xcdd,0xedc'
TOTAL_NOVICES = '0xee8,0xc0a,0xe4d,0xbf0,0xc17,0xe59,0xc52,0x990,0x920,0xec1,0xda3,0x960,0xd4b,0xcc5,0xa9a,0xbe3,0xe5c,0xe04,0xd5c,0x9e0,0xc89,0xc82,0xa50,0xc9d,0xa10,0xdb8,0x910,0xcb4,0xbb3,0xd94,0xc1e,0xdac,0xe94,0xece,0xc76,0xd31,0xc70,0xbd1,0xc34,0xb7a,0xea2,0xea0,0xdc9,0xd76,0xe79,0xea8,0xca4,0xc3d,0xce4,0xdde,0xbc0,0xbc7,0xcdd,0xedc,0xa70,0xc67,0xd4d,0xc25,0xa30,0x930,0xdd2,0xe8b,0xed0'

BAD_BLOCKS = [0x400bc7, 0x400c1e, 0x400c8e, 0x400ca2, 0x400c9d, 0x400c89,   # main
              0x400e94, 0x400ea0, 0x400ee8]                                 # bridge


def adapt(bb_time_list, key_list):
    res = {k : 0.0 for k in key_list.split(',')}
    for offs in bb_time_list:
        if offs in res:
            res[offs] = bb_time_list[offs]
    return res
        

def create_dot_file(graph, output):
    import networkx
    networkx.drawing.nx_pydot.write_dot(graph, output)


def remove_entities(graph, entities):
    for entity in entities:
        if type(entity) is angr.knowledge_plugins.cfg.cfg_node.CFGNode:
            graph.remove_node(entity)


def edit_graph(graph):
    # 0xe08, 0xe60 
    offsets = [GET_ADDR(offset) for offset in OFFSETS] + [GET_ADDR(offset)-4 for offset in [ 0xe08, 0xe60 ]]
     
    nodes_to_remove = [node for node in graph.nodes if node.function_address not in offsets]
    remove_entities(graph, nodes_to_remove)
    return graph


class GraphPlotter():

    def __init__(self, filename, output_path = '/tmp/cfg'):
        self.filename = filename
        self.output_path = os.path.join(output_path, 'plot.cfg')
        p = angr.Project(filename, load_options={'auto_load_libs': False})
        cfg = p.analyses.CFG()
        graph = cfg.graph
        graph = edit_graph(cfg.graph)
        create_dot_file(graph, self.output_path)


    def plot(self, non_interesting_experts, non_interesting_novices, bbs_times_experts, bbs_times_novices, normalize = True):
        # making the graph cool
        if normalize:
            no_int_exp = adapt(non_interesting_experts, NON_INTERESTING_EXPERTS)
            no_int_nov = adapt(non_interesting_novices, NON_INTERESTING_NOVICES)
            times_exp = adapt(bbs_times_experts, TOTAL_EXPERTS)
            times_nov = adapt(bbs_times_novices, TOTAL_NOVICES)
        else:
            no_int_exp = non_interesting_experts
            no_int_nov = non_interesting_novices
            times_exp = bbs_times_experts
            times_nov = bbs_times_novices

        gd = GraphDecorator(self.output_path, no_int_exp, no_int_nov, times_exp, times_nov)
        gd.colour_edges()
        gd.colour_nodes()
        gd.draw(self.output_path)


class GraphDecorator():

    def __init__(self, filepath, non_interesting_experts, non_interesting_novices, bbs_times_experts, bbs_times_novices):
        self.g = pgv.AGraph(filepath)
        self.g.node_attr['style'] = 'filled'
        self.g.node_attr['fillcolor'] = 'white'
        self.g.node_attr['label'] = ' ' * LABEL
        self.g.node_attr['shape'] = 'box'
        self.g.node_attr['rank'] = 'source'
        self.non_interesting_experts = non_interesting_experts
        self.non_interesting_novices = non_interesting_novices

        times_experts = self.clean_time_dictionary(bbs_times_experts, non_interesting_experts)
        times_novices = self.clean_time_dictionary(bbs_times_novices, non_interesting_novices)

        self.interesting_experts = times_experts
        self.interesting_novices = times_novices

        OFFSETS.sort()


    def clean_time_dictionary(self, times_bbs, non_interesting_times_bbs):
        for bb in non_interesting_times_bbs:
            if bb in times_bbs:
                del times_bbs[bb]
        return times_bbs

    #def get_addr_by_node(self, node_name):
    #    start = len('CFGNode ')
    #    if '_' in node_name:
    #        start = node_name.index('_') + 1
    #    print(node_name)
    #    #start = node_name.index('_')
    #    end = start + 6
    #    return int(node_name[start : end], 16)
    def get_addr_by_node(self, node_name):
        end = node_name.index('[')
        fcn_name_offs = node_name[len('CFGNode ') :  end]

        if '+' in fcn_name_offs:
            fcn_name, offset = fcn_name_offs.split('+')
        else:
            fcn_name = fcn_name_offs
            offset = '0x0'

        if '_' in fcn_name:
            return  int(fcn_name.split('_')[1], 16) + int(offset, 16)
        else:
            if 'main' in fcn_name:
                return 0x400b7a + int(offset, 16)
            return None



    def is_interesting(self, node_addr):
        elem = 0
        for i in range(0, len(OFFSETS) - 2):
            starting_addr = OFFSETS[i]
            ending_addr = OFFSETS[i + 1]
            if node_addr in BAD_BLOCKS:
                return False
            if node_addr >= GET_ADDR(starting_addr) and node_addr < GET_ADDR(ending_addr):
                return starting_addr in INTERESTING
        return OFFSETS[-1] in INTERESTING


    def colour_edges(self):
        for edge in self.g.edges():

            dst = self.get_addr_by_node(edge[1])
            if self.is_interesting(dst):
                edge.attr['color']= 'green'

            else:
                edge.attr['color'] = 'red'
                #edge.attr['style'] = 'dotted'



    def look_for_right_offset(self, offs, time_dict):
        if offs in time_dict:
            return time_dict[offs]
        elif hex(int(offs, 16) - 4) in time_dict:
            return time_dict[hex(int(offs, 16) - 4)]
        else:
            return 0


    def colour_nodes(self):
        for node in self.g.nodes():

            addr = self.get_addr_by_node(node)
            offs = GET_OFFSET(addr)

            if offs in self.non_interesting_experts or offs in self.non_interesting_novices:
                expert_time = self.non_interesting_experts[offs] if offs in self.non_interesting_experts else 0
                novice_time = self.non_interesting_novices[offs] if offs in self.non_interesting_novices else 0
                scale_function = GET_RGB
            else:
                #expert_time = self.interesting_experts[offs] if offs in self.interesting_experts else 0
                #novice_time = self.interesting_novices[offs] if offs in self.interesting_novices else 0
                expert_time = self.look_for_right_offset(offs, self.interesting_experts)
                novice_time = self.look_for_right_offset(offs, self.interesting_novices)
                scale_function = GET_RGB
                #import ipdb; ipdb.set_trace()

            # Enable the following line for static choice of colors
            #exp_col, nov_col = self.colour_node_by_time_statically(expert_time, novice_time)
            if expert_time != 0 or novice_time != 0:
                exp_col, nov_col = self.colour_node_by_time_dynamically(expert_time, novice_time, scale_function)
                node.attr['label'] = ' ' * LABEL
                node.attr['fillcolor'] = '{0};0.5:{1};0.5'.format(exp_col, nov_col)


    def get_percentages(self, bbs_times):
        total_time = sum(bbs_times.values())
        return {k: bbs_times[k]/total_time for k in bbs_times}



    def colour_node_by_time_statically(self, expert_time, novice_time):
        expert_idx = self.get_colour_idx(expert_time)
        novice_idx = self.get_colour_idx(novice_time)
        return COLORS[expert_idx], COLORS[novice_idx]


    def colour_node_by_time_dynamically(self, expert_time, novice_time, scale_function):
        r_code = scale_function(expert_time)[2:4].zfill(2)    # for experts shades of green
        b_code = scale_function(novice_time)[2:4].zfill(2)    # for novices shades of blue

        r_code = r_code.replace('x', '0')
        b_code = b_code.replace('x', '0')


        exp_col = "#" + 'ff'     + r_code + r_code
        nov_col = "#" + b_code + b_code + 'ff'
        return exp_col, nov_col


    def get_colour_idx(self, time):
        idx = int(time / 20)
        if idx > 4:
            idx = 4
        return idx

    def draw(self, output):
        #import ipdb; ipdb.set_trace()
        #self.g.layout(prog='dot')
        self.g.layout(prog='dot')
        #import ipdb; ipdb.set_trace()
        #self.g.pack = True
        self.g.draw(output + '.pdf')


