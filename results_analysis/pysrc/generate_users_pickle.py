#!/usr/bin/env python

import os
from base.initialize import setup, setup_redefinition
import pickle
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
pickle_file = os.path.join(dir_path, '../pickle/users_data.p')

novices, experts, all_users = setup_redefinition()

assert(len(all_users.all_users) > 0)

with open(pickle_file, 'wb') as f:
    pickle.dump(all_users, f)
