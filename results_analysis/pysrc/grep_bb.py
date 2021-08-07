#!/usr/bin/env python

from base.pickle_loader import load_splitted_by_redefinition, load
from base.initialize import setup_redefinition, reputation_heuristic
import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))

bb_addr = sys.argv[1]
print(bb_addr)
bbs = load(os.path.join(dir_path, '../pickle/basic_blocks.p'))

for bb in bbs:
    if bb.address == bb_addr:
        print(f"Task: {bb.task}")
        print(f"Len: {bb.instructions}")
        print(f"Type: {bb.type}")


