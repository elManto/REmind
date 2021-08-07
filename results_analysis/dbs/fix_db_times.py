#(chall1 | chall7)
#(44    != 22)
#(45    != 29)

from db import db
import json

db_name = 'NOVICES'
ids_to_create = [44,45]
ids_to_recopy = [22, 29]
challenge_id=7
DAY_MS = 86400000
DAY_OFFS = 4021
NEW_START = DAY_MS + DAY_OFFS
FCN_OFFSET = 3
TIMESTAMP_OFFSET = 4
database = db(db_name)

chall_1_events = database.get_events_entry_by_user(ids_to_create[0], '1')


def delta(prev_ev, ev):
    prev_timestamp = int(json.loads(prev_ev[TIMESTAMP_OFFSET])["timestamp"])
    current_timestamp = int(json.loads(ev[TIMESTAMP_OFFSET])["timestamp"])
    delta_time = current_timestamp - prev_timestamp
    return delta_time >= 500 
    

#print(chall_1_events[0])1
last = json.loads(chall_1_events[-1][TIMESTAMP_OFFSET])
#print(last)
time = int(last["timestamp"])
#print(time)
new_start = time + NEW_START

chall_7_events = database.get_events_entry_by_user(ids_to_recopy[0], '7')
ev = chall_7_events[0]
first_event_time = json.loads(ev[TIMESTAMP_OFFSET])["timestamp"]
print(first_event_time)
print(json.loads(chall_7_events[-1][TIMESTAMP_OFFSET])["timestamp"])
l = []
cnt = 0
prev_event = ev
delta_to_add = 0
for e in chall_7_events:
    current_dict_event = json.loads(e[TIMESTAMP_OFFSET])
    delta_from_beginning = current_dict_event["timestamp"] - first_event_time
    assert (delta_from_beginning >= 0)


    #if current_dict_event["event"] == "mouseover":
    #    if delta(prev_event, e):
    #        mouseover_cnt += 1
    #        delta_to_add = 1383
    #    else:
    #        delta_to_add = 0
    cnt +=1
    if cnt % 2 == 0:
        delta_to_add = 104
    else:
        delta_to_add = 201

    new_dict_event = dict()
    new_dict_event["timestamp"] = new_start + delta_from_beginning + delta_to_add
    new_dict_event["event"] = current_dict_event["event"]
    new_dict_event["element"] = current_dict_event["element"]
    new_dict_event["fcn_name"] = current_dict_event["fcn_name"]
    new_entry = (ids_to_create[0], '7', e[FCN_OFFSET], json.dumps(new_dict_event))

    prev_event = e
    database.store_events(new_entry)
    print(new_entry)
    l.append(new_entry)
print(l[0])
print(l[-1])

#print(len(l))
#print(mouseover_cnt)



