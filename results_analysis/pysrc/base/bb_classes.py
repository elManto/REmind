import os
import json
from enum import Enum
from .user_classes import UserKind

ANGR_OFFSET = 0x400000


class NodeType(Enum):   # Self-explainatory, a simple enum to divide BBs in three types according to
    HEADER = 1          # their position in the function
    FOOTER = 2
    OTHER = 3


class UserViews():      # Represents the Views for a certain user on a specific BB, i.e., for each
                        # time the user `U` visit the BB `b`, we add an item to the list 'self.times'

    def __init__(self, times, kind, uid):
        self.uid = ""       # Just a string, not so useful
        self.kind = kind    # If the 'UserViews' belongs to an 'Expert' or a 'Novice'. Note that respect to
                            # the initial division between 'Expert` and 'Novices', this is quite agnostic
                            # from it , since it's just about using the 'original_kind' or 'redefinition'
                            # field that lives in the User class

        self.times = times  # As already explained, list containing the times for each visit on a
                            # specific BB. Finally notice that the BB information is not contained
                            # in this class, but instead, it is embedded in the BB class

        self.uid = uid      # The field uid refers to a user identifier unique in our system.
                            # uid is the concatenation of db name + user id in that db


    def set_uid(self, uid):
        self.uid = uid


    def is_expert(self):
        return self.kind == UserKind.EXPERT




class BB():                 # Describes the info related to a BB as well as the users interactions (in
                            # terms of visits) with it

    def __init__(self, addr, fcn_name, type, list_of_user_views, distance, instructions, challenge_id):

        self.fields = dict()                    # Originally created to iterate on the fields easily, now
                                                # basically useless but shouldn't create further issues

        self.address = hex(addr)                # BB address
        self.function = fcn_name                # Function name that contains the BB

        #for idx, user_view in enumerate(list_of_user_views):
        #    if not user_view.is_expert():
        #        uid = 'Novice{0}'.format(idx)   # 'list_of_user_views' is a list of 'UserViews' for each
        #                                        # user who visited at least one time that BB.
        #    else:                               
        #        uid = 'Expert{0}'.format(idx)
        #    user_view.set_uid(uid)

        self.user_views = list_of_user_views            # list of views for the current
                                                        # BB for each user
        self.task = '1' if challenge_id == 1 else '2'
        self.type = type.name                           # See the Enum type
        self.distance = str(distance)                   # Distance from the path for the solution
        self.instructions = str(instructions)           # Number of instructions


    def get_offset(self):
        addr = int(self.address, 16)
        offs = hex(addr - ANGR_OFFSET)
        return offs
