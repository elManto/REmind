import r2pipe
import json
from base64 import b64decode
import sys

output_path = ''
d = dict()
angr_offset = int('0x400000', 16) # NOTE! Remember to change it you're handling a Position Indipendent executable

if __name__ == '__main__':
    filename = sys.argv[1]
    output_path = sys.argv[2] + '/'

    f = open(output_path + 'offset.json', 'r')
    d = json.loads(f.readlines()[0])
    debugged = r2pipe.open(filename)
    debugged.cmd('aaa')
    strings = json.loads(debugged.cmd('izj'))
    string_dict = dict()
    for line in strings:
        vaddr = hex(int(line['vaddr']))
        i = 0
        c = vaddr[i]
        while(c == '0' or c == 'x'):
            i += 1
            c = vaddr[i]
        print("vaddr->" + vaddr[i:])
        xrefs_to_string = debugged.cmd('axtj@' + "0x" + vaddr[i:])
        xref_dict = json.loads(xrefs_to_string[:-1])
        xref_list = []
        addr_list = []
        opcode_list = []
        print(xref_dict)
        for xref in xref_dict:
            # here we put the function that uses the string
            print(xref)
            if 'fcn_name' in xref:
                ret = xref['fcn_addr']
                #print(ret.split('.')[-1])
                if ret != "":
                    addr_list.append(hex(xref['from'] + angr_offset))
                    func_addr = hex(ret + angr_offset)
                    my_function_name = 'sub_{0}'.format(func_addr[2:])  # this is to remove 0x from the function name (so we get sub_400ab3 instead of sub_0x400ab3)
                    xref_list.append(my_function_name)
                    opcode_list.append(xref['opcode'])
        print(xref_list)
        # se xref_list vuota non considerare, altrimenti aggiungu al dict
        xref_dict = {"xref" : xref_list}
        addr_dict = {"addr" : addr_list}
        opcode_dict = {"opcode" : opcode_list}
        val_dict = {"str": b64decode(line['string']).decode('utf-8')}
        if len(xref_list) >= 1:
            # real_vaddr = hex(int(vaddr, 16) + angr_offset)
            string_dict[vaddr] = [xref_dict, val_dict, addr_dict, opcode_dict]
    print(string_dict)
    with open(output_path + 'strings.json', 'w') as strings_fd:
        strings_fd.write(json.dumps(string_dict))

    info = json.loads(debugged.cmd('ij'))
    info_dict = info["core"]
    for key in info["bin"]:
        info_dict[key] = info["bin"][key]
    open(output_path + 'info.json', 'w').write(json.dumps(info_dict))

