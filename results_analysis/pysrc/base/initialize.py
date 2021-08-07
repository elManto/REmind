import configparser
from .user_classes import User, AllUsers, UserKind
from .usersDBHandler import UserHandlers

def generate_user(a_priori_users):
    users = []
    for user_1, user_7 in a_priori_users.join_challs_by_user():
        events_1 = user_1.process_events()
        events_7 = user_7.process_events()
        lev = user_1.get_level()
        uid = user_1.user_id
        if uid != user_7.user_id:
            print("[Warning] user ids different ({0} != {1})".format(uid, user_7.user_id))
        else:
            print("[InfoDB] user ids equivalent ({0} == {1})".format(uid, user_7.user_id))
        if lev != user_7.get_level():
            print("[Warning] levels for a user are different")
        user_id = user_1.user_id
        u = User(lev, user_1.db + str(user_id), a_priori_users.original_kind)
        u.set_challenge_statistics('1', events_1)
        u.set_challenge_statistics('7', events_7)
        users.append(u)
    return users

def setup():

    a_priori_experts = UserHandlers(UserKind.EXPERT)
    a_priori_novices = UserHandlers(UserKind.NOVICE)

    config = configparser.ConfigParser()
    config.read('../dbs/config.ini')

    for section in config.sections():
        challenge_id = section[-1]
        users = config[section]['users'].split(',')
        db_name = config[section]['name']
        assert(len(users) > 0)
        assert(challenge_id == '1' or challenge_id == '7')
        if section.startswith('EXPERTS'):
            a_priori_experts.collect_users_from_db(challenge_id, db_name, users)
        elif section.startswith('NOVICES'):
            a_priori_novices.collect_users_from_db(challenge_id, db_name, users)
        else:
            print("Section with name {0} not implemented".format(section))    

    students = generate_user(a_priori_novices)
    players = generate_user(a_priori_experts)
    all_users = AllUsers(students + players) 
    return students, players, all_users


# The "worst expert time" heuristic (the current default) divides the users according to
# a time threshold which is defined by the "worst" solution time collected among the
# experts who do RE tasks at least "often"
def worst_expert_time_heuristic():
    students, players, all_users = setup()

    time_threshold = 0
    for user in students + players:
        if user.get_solution_time() > time_threshold and user.level >= 3 :
            time_threshold = user.get_solution_time()

    new_novices = []
    new_experts = []
    for user in all_users.all_users:
        if user.get_solution_time() <= time_threshold:
            user.redefinition = UserKind.EXPERT
            new_experts.append(user)
        else:
            user.redefinition = UserKind.NOVICE
            new_novices.append(user)

    return new_novices, new_experts, all_users


# This heuristic just copies the expertise level as it is
def reputation_heuristic():
    students, players, all_users = setup()
    for user in all_users.all_users:
        user.redefinition = user.original_kind
    return students, players, all_users


# This function takes as input a function that implements an heuristic to
# separate novices / experts according to some new definition
def setup_redefinition(heuristic_function = worst_expert_time_heuristic):
    students, players, all_users = heuristic_function()
    return students, players, all_users
   
