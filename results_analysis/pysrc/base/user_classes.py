from enum import Enum

class UserKind(Enum):
    EXPERT = 1
    NOVICE = 2


class User():
    
    def __init__(self, level, user_id, original_kind):
        self.original_kind = original_kind  # It defines if the user is a `Novice` or a `Expert`
                                            # relying on the 'reputation' i.e., when we contacted them

        self.redefinition = ''              # It will be set later when we decide the threshold, but the field stores the 'new'
                                            # definition of the user (either `Novice` or `Expert`) given the heuristic adopted. 
                                            # Refer to initialize.py for an example of threshold usage

        self.level = level                  # Stores the answer to the self-evaluation question
        self.user_id = user_id              # A UNIQUE user id that represents the ID in the db concatenated with the db name
        self.chall = {'1' : None, '7' : None}   # A simple dict that will host the info related to the challs, e.g., two objects of the class `ChallengeStatistics`

    
    def set_challenge_statistics(self, challenge_id, statistics):
        views = statistics[0]               # list containing the intervals of time spent on each BB
        addresses = statistics[1]           # list containing the integer numbers representing the visited offsets within the binary
        sol_time = statistics[2]            # overall solution time for the challenge with id `challenge_id`
        transitions = statistics[3]         # number of transition between different BBs 
        raw_events = statistics[4]          # list of json events as they 're stored in the DB
        assert(len(views) > 0)
        assert(len(addresses) > 0)
        self.chall[challenge_id] = ChallengeStatistics(challenge_id, views, addresses, sol_time, transitions, raw_events)

    def get_level(self):
        return self.level

    def get_solution_time(self, per_chall = None):  # if `per_chall` is not specified, we return the overall solution time for both the challenges
        if per_chall == None:
            return self.chall['1'].sol_time + self.chall['7'].sol_time
        else:
            chall_id = str(per_chall)
            assert (chall_id == '1' or chall_id == '7')
            return self.chall[chall_id].sol_time    # else we return the solution time for a specific chall identified by `per_chall` id


    def get_visited_bbs(self, per_chall = None):    # similar to the previous method, but it returns the overall (or per single chall) number of transitions (i.e., movements between the BBs)
        if per_chall == None:
            return self.chall['1'].transitions + self.chall['7'].transitions
        else:
            chall_id = str(per_chall)
            assert (chall_id == '1' or chall_id == '7')
            return self.chall[chall_id].transitions


class ChallengeStatistics():
    
    def __init__(self, challenge_id, views, addresses, sol_time, transitions, raw_events):
        self.challenge_id = challenge_id
        self.views = views
        self.addresses = addresses
        self.sol_time = sol_time
        self.transitions = transitions
        self.raw_events = raw_events    # represente list of json containing each single event
    

class AllUsers():                       # Simple (and almost useless) class that includes ALL the users (i.e., both experts and novices). SOmetimes it's easier to iterate over a single list 
                                        # rather than two separated loops , one for experts and the other for novices
    
    def __init__(self, list_of_users = None):
        if list_of_users == None:
            self.all_users = []
        else:
            self.all_users = list_of_users
    
        
    def add_users(self, new_users):
        self.all_users += new_users

    
    def get_user_by_id(self, uid):
        for u in self.all_users:
            if u.user_id == uid:
                return u
        return None
