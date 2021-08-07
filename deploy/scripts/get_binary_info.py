import angr
import json
import sys

json_out = dict()
call_map = dict()
analysed_func = []
xrefs_from = dict() # key->bb which is called; value->list of bb which call the key
xrefs_to = dict()
func_offset = dict()
end_offset = 0
output_path = '' 

def getFunctionNames(functions):
    return [f[1].name for f in functions]
             

def disasmBlock(addr, func):
    global end_offset
    disasm = p.factory.block(addr).capstone.insns
    s = ''
   
    for insn in disasm:
        # first if-else is for building the xrefs
        if(insn.mnemonic == "call"):
            if insn.op_str in call_map.keys():
                call_name = call_map[insn.op_str]
                if not func in xrefs_from[call_name]:
                    xrefs_from[call_name].append(func + "@" + hex(int(addr)))
                if not call_name in xrefs_to[func]:
                    xrefs_to[func].append(call_name)
        if(insn.mnemonic == "jmp"):
            if insn.op_str in call_map.keys(): 
                call_name = call_map[insn.op_str]
                if not func in xrefs_from[call_name]:
                    xrefs_from[call_name].append(func)
                if not call_name in xrefs_to[func]:
                    xrefs_to[func].append(call_name)
   

        # second if-else is for render the disassembly
        if(insn.mnemonic == "call"):
            if insn.op_str in call_map:
                call_name = call_map[insn.op_str]
                s += hex(int(insn.address)) + ": " + insn.mnemonic + " " + call_name + "\n"
            else: 
                s+= hex(int(insn.address)) + ": " + insn.mnemonic + " " + insn.op_str + "\n"
        elif(insn.mnemonic == "jmp"):
            if insn.op_str in call_map.keys(): 
                s += hex(int(insn.address)) + ": " + insn.mnemonic + " " + call_map[insn.op_str] 
            else: 
                s += hex(int(insn.address)) + ": " + insn.mnemonic + " " + insn.op_str + "\n"
        else:
            s+= hex(int(insn.address)) + ": " + insn.mnemonic + " " + insn.op_str + "\n"
        
        if(int(insn.address) > end_offset):
            end_offset = int(insn.address)
    return s

def functionInfo(functions):
    for f in functions:
        print(f)

def mainCFG(functions):
    l = []
    for f in functions:
        if (f[1].name == 'main'):
            func_main = f[1] 
            l = [k for k in f[1].block_addrs]
            break
    l.sort()
    total_blocks = {}
    total_edges = {}
    edge_list = []
    for bb in l:
        #print "basick block @ " + str(bb)
        disasm = disasmBlock(bb)
        total_blocks[hex(int(bb))] = disasm
    #print "now edges +++++++"
    for edge in list(func_main.graph.edges):
        first_v = hex(int(edge[0].addr))
        second_v = hex(int(edge[1].addr))
        edge_list.append([first_v, second_v])
        #print str(first_v) + " -> " + str(second_v)
    total_edges["edges"] = edge_list
    json_out["main_edges"] = total_edges
    json_out["main_bbs"] = total_blocks


def fillCallMap(functions):
    tmp = []
    for f in functions:
        if (not f[1].name in tmp):
            tmp.append(f[1].name)
            call_map[hex(int(f[0]))] = f[1].name


def CFG(functions):
    l = []
    for f in functions:
        if (not f[1].name in analysed_func):
            start_offset = hex(int(f[0]))
            global end_offset 
            analysed_func.append(f[1].name)
            #call_map[hex(int(f[0]))] = f[1].name
            json_out = dict()
            name = f[1].name 
            l = [k for k in f[1].block_addrs]
            # print f[1].name
            l.sort()
            total_blocks = {}
            total_edges = {}
            edge_list = []
            
            for bb in l:
                disasm = disasmBlock(bb, f[1].name)
                total_blocks[hex(int(bb))] = disasm
            func_offset[f[1].name] = {"start" : start_offset, "end" : hex(end_offset)}
            end_offset = 0
            for edge in list(f[1].graph.edges):
                first_v = hex(int(edge[0].addr))
                second_v = hex(int(edge[1].addr))
                edge_list.append([first_v, second_v])
            total_edges["edges"] = edge_list
            json_out[name + "_edges"] = total_edges
            json_out[name + "_bbs"] = total_blocks
            file_out = open(output_path + name + '.json', 'w')
            file_out.write(json.dumps(json_out))
            file_out.close()


if __name__ == '__main__':
    filename = sys.argv[1]
    output_path = sys.argv[2] + "/"

    p = angr.Project(filename, load_options={'auto_load_libs': False})
    cfg = p.analyses.CFG()
    functions = cfg.kb.functions.items()


    fillCallMap(functions)
    for key in call_map:
        xrefs_from[call_map[key]] = []
        xrefs_to[call_map[key]] = []
    CFG(functions)

    fcs = open(output_path + 'functions.json', 'w')
    functionNames = getFunctionNames(functions)
    for fc in functionNames:
        fcs.write(fc + "\n")
    # print(call_map)
    #for key in xrefs_from:
    #    print key,
    #    print xrefs_from[key]
    xrefs_from_json = open(output_path + "xrefs_from.json", "w")
    xrefs_from_json.write(json.dumps(xrefs_from))

    xrefs_to_json = open(output_path + "xrefs_to.json", "w")
    xrefs_to_json.write(json.dumps(xrefs_to))

    # now we generate the callgraph
    callgraph = cfg.functions.callgraph
    callgraph_dict = dict()
    callgraph_dict['nodes'] = [[hex(int(node_addr)), call_map[hex(int(node_addr))]] for node_addr in list(callgraph.nodes) if hex(int(node_addr)) in call_map.keys()]
    callgraph_dict['edges'] = []
    for edge in list(callgraph.edges):
        if ((hex(int(edge[0])) in call_map.keys()) and (hex(int(edge[1])) in call_map.keys())):
            callgraph_dict['edges'].append([hex(int(edge[0])), hex(int(edge[1]))])
    callgraph_json = open(output_path + "callgraph.json", 'w')
    callgraph_json.write(json.dumps(callgraph_dict))
    offset=open(output_path + "offset.json", "w")
    offset.write(json.dumps(func_offset))
