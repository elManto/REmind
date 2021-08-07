import r2pipe
import json
from base64 import b64decode
import sys

output_path = './flask_website/json/'
f = open(output_path + 'offset.json', 'r')
d = json.loads(f.readlines()[0])
angr_offset = int('0x400000', 16) # NOTE! Remember to change it you're handling a Position Indipendent executable

def getStringXref(hex_addr):
    print hex_addr
    addr = int(hex_addr, 16)
    for key in d:
        if (addr + angr_offset >= int(d[key]["start"], 16) and addr + angr_offset <= int(d[key]["end"], 16)):
            return key
    return ""


if __name__ == '__main__':
    filename = sys.argv[1]
     
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
        print vaddr
        xrefs_to_string = debugged.cmd('/cj ' + vaddr[i:])
        xref_dict = json.loads(xrefs_to_string[:-1])
        xref_list = []
        addr_list = []
        print xref_dict
        for xref in xref_dict:
            ret = getStringXref(hex(xref["offset"])) 
            if ret != "":
                addr_list.append(hex(xref["offset"] + angr_offset))
                xref_list.append(ret)
        print xref_list
        # se xref_list vuota non considerare, altrimenti aggiungu al dict
        xref_dict = {"xref": xref_list}
        addr_dict = {"addr": addr_list}
        val_dict = {"str": b64decode(line['string'])}
        if len(xref_list) >= 1:
            string_dict[vaddr] = [xref_dict, val_dict, addr_dict]
    open(output_path + 'strings.json', 'w').write(json.dumps(string_dict))

    info = json.loads(debugged.cmd('ij'))
    info_dict = info["core"]
    for key in info["bin"]:
        info_dict[key] = info["bin"][key]
    open(output_path + 'info.json', 'w').write(json.dumps(info_dict))

