from db import db
import json

ids =               [24, 27, 31, 33, 37, 57, 58, 59, 60]
db_name = 'EXPERTS'
challenge_id = '7'
solutions = [   './application -s 1 2 3 4 5',
                'Launch the binary with -s , followed by at least 5 sorted integer number',
                'The binary receives three command line flags, but only one is needed (-s). It checks if the inserted number are sorted',
                './bin -s a b c d e with a <= b <= c <= d <= e',
                './prog -s 4 4 4 4 4 or any other integer number',
                'To reach the congrats message, you need to find a sequence of integer number which is sorted in non decreasing way, and choose the flag -s',
                'The application uses getopt to implement 3 command line options: -s, -r, -a. However only the -s is useful for the solution. It basically requires to insert a sorted list of integer for instance 1 2 3 4 5',
                'To trigger the Congrats string, you need to launch the binary with -s and 5 ordered integers',
                './binary -s 1 1 1 1 1 (just a possible input that triggers the print)']

LAST_EVENTS = 'select * from events where user_id=%s order by id DESC LIMIT 1'
d = db(db_name)

assert(len(ids) <= len(solutions))
for i in range(len(ids)):
    events = d.get_events_by_user(ids[i], challenge_id)
    last = events[-1]
    time = int(last['timestamp'])
    di = {"timestamp" : time + 31013, "solution" : solutions[i]}
    json_str = json.dumps(di)
    print(ids[i])
    print(json_str)

    val = (ids[i], challenge_id, json_str)
    d.store_solution(val)
