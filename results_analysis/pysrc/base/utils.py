from .config import config_dictionary


MAX_TIME = config_dictionary['max_time']
MIN_TIME = 500


class User():

    def __init__(self, uid):
        self.uid = uid
        self.fields = dict()


    def set_fields(self, spider_graph_stats, transitions, discarded_bbs_via_glance, time_for_useless_stuff, glances_quarters, total_time, average_time_per_bb):
        #self.fields['uid'] = self.uid
        #self.fields['static_glances'] = round(spider_graph_stats[0], 2)
        self.fields['first_true'] = round(spider_graph_stats[1], 2)
        self.fields['first_close'] = round(spider_graph_stats[2], 2)
        #self.fields['first_back'] = round(spider_graph_stats[3], 2)
        #self.fields['out'] = round(spider_graph_stats[4], 2)
        #self.fields['vertical'] = round(spider_graph_stats[5], 2)
        #self.fields['horizontal'] = round(spider_graph_stats[6], 2)
        #self.fields['back_forth'] = round(spider_graph_stats[7], 2)
        #self.fields['transitions']  = round(transitions, 2)

        #discard_glances = round(discarded_bbs_via_glance, 2)
        
        #self.fields['discarded_bbs_via_glance'] = discard_glances
        #time_for_useless_stuff = round(time_for_useless_stuff, 2) if time_for_useless_stuff > 0.1 else 3.1
        #self.fields['time_for_useless_stuff'] = time_for_useless_stuff
        #self.fields['percentage_useless_time'] = time_for_useless_stuff / float(total_time)
        # For now we dont consider glances divided in the time quarters
        # since it doesnt provide any meaningful result
        #self.fields['glances_1'] = round(glances_quarters[0], 2)
        #self.fields['glances_2'] = round(glances_quarters[1], 2)
        #self.fields['glances_3'] = round(glances_quarters[2], 2)
        #self.fields['glances_4'] = round(glances_quarters[3], 2)
        self.fields['total_time'] = round(total_time, 2)
        #self.fields['avg_time_bb'] = round(average_time_per_bb, 2)


    def set_fields_shallow_deep(self, other_fields):
        #self.fields['short_view_time(ms)'] = other_fields[0]
        #self.fields['long_view_time(ms)'] = other_fields[1]
        #self.fields['number_bb_short'] = int( other_fields[5] * self.fields['transitions'])
        #self.fields['number_bb_medium'] = int(other_fields[6] * self.fields['transitions'])
        #self.fields['number_bb_long'] = int( other_fields[7] * self.fields['transitions'])
        #self.fields['ratio_bb_short'] = round(other_fields[5], 2)
        #self.fields['ratio_bb_medium'] = round(other_fields[6], 2)
        #self.fields['ratio_bb_long'] = round(other_fields[7], 2)
        #self.fields['delta_views(ms)'] = round(other_fields[8], 2)
        return


    def get_field_names(self, limit = None, end = None):
        names =  [k for k in self.fields]
        if limit == None or limit > len(names):
            return names
        elif limit != None and end == None:
            return names[0:limit]
        else:
            return names[limit : end]


    def get_fields(self, limit = None, end = None):
        if limit == None or limit > len(self.fields):
            return self.fields
        elif limit != None and end == None:
            return self.fields[0 : limit]
        else:
            return self.fields[limit : end]


    def tabularize(self, limit = None, end = None):
        fields = [self.fields[k] for k in self.fields]
        if limit == None or limit > len(fields):
            return fields 
        elif limit != None and end == None:
            return fields[0 : limit]
        else:
            return fields[limit : end]



def scale_vector(v, isAddress):
    mi = min(v[:-1])
    if isAddress:
        mi = config_dictionary['binary1']['base']
    for i in range(len(v)):
        v[i] = v[i] - mi
    return v


def scale_size(v):
    mi = min(v)
    ma = max(v)
    for i in range(len(v)):
        v[i] = 100*v[i]/ma
    return v


def generate_vectors(events, scale=True, hex_addresses=False, challenge_id = -1):
    if challenge_id == -1:
        base = config_dictionary['binary1']['base']
        end = config_dictionary['binary1']['base'] + config_dictionary['binary1']['length']
    else:
        base = 4196624 if challenge_id == 1 else 4196096
        length = 1600 if challenge_id == 1 else 1900
        end = base + length
    x = []
    y = []
    s = []
    zero_event = events[1]
    start_time = zero_event['timestamp']
    remove_pause = 0
    for i in range(2, len(events) - 2):
        if events[i]['event'] == 'function_visit':
            continue

        delta_time = events[i]['timestamp'] - start_time
        if delta_time > MAX_TIME or 'pause' == events[i]['event']:
            start_time = events[i]['timestamp']
            remove_pause += delta_time
            continue
        if not 'element' in events[i]:
            continue
        elem = events[i]['element']
        if events[i]['event'] == 'mouseover':
            start_time = events[i]['timestamp']
            address = int(events[i]['element'], 16)
            
            if address >= base and address < end and abs(delta_time) >= 500:
                x.append(start_time - remove_pause)
                y.append(address)
                s.append(abs(delta_time))

    x = scale_vector(x, False)
    if not hex_addresses:
        y = scale_vector(y, True)
    else:
        y = [hex(addr) for addr in y]
    if scale:
        s = scale_size(s)


    return [x, y, s]


def fetch_times(events, challenge_id = -1):
    if challenge_id == -1:
        base = config_dictionary['binary1']['base']
        end = config_dictionary['binary1']['base'] + config_dictionary['binary1']['length']
    else:
        base = 4196624 if challenge_id == 1 else 4196096
        length = 1600 if challenge_id == 1 else 1900
        end = base + length

    transitions = 0
    zero_event = events[1]
    start_time = zero_event['timestamp']
    begin = start_time
    remove_pause = 0
    res = []
    addresses = []
    for i in range(2, len(events)):
        if events[i]['event'] == 'function_visit':
            continue

        if events[i]['event'] == 'mouseover':
            delta_without_pauses = events[i]['timestamp'] - start_time
            if delta_without_pauses > MAX_TIME or 'pause' == events[i]['event']:
                remove_pause += delta_without_pauses

            delta_time = events[i]['timestamp'] - start_time
            if delta_time < 500:
                continue
            address = int(events[i]['element'], 16)
            start_time = events[i]['timestamp']
            total_time = events[i]['timestamp'] - begin
            base = config_dictionary['binary1']['base']
            end = config_dictionary['binary1']['base'] + config_dictionary['binary1']['length']
            if address >= base and address < end:
                transitions += 1
                addresses.append(address)
                res.append(delta_time)
    return res, addresses, total_time - remove_pause, transitions



def convert_to_minutes(milliseconds):
    return milliseconds/(1000*60)


def compare_function_times(foo_list, cfg_dict, addresses, times):
    res = {k : 0 for k in foo_list}
    for addr, t in zip(addresses, times):
        for foo in foo_list:

            if hex(addr) in cfg_dict[foo]:
                res[foo] += 1
    return res


def discarded_via_glimpse(times, addresses, glimpse_value):
    bb_dict = {}
    threshold = glimpse_value if glimpse_value > 0 else config_dictionary['glance_static_interval']
    for i in range(min(len(addresses), len(times))):
        addr = addresses[i]
        is_glimpse = True if times[i] < threshold else False
        if addr in bb_dict:
            bb_dict[addr]['freq'] += 1
        else:
            bb_dict[addr] = {'freq' : 1, 'is_glimpse' : is_glimpse}

    discarded = 0
    visited_once = 0
    for bb in bb_dict:
        if bb_dict[bb]['freq'] == 1:
            visited_once += 1
            if bb_dict[bb]['is_glimpse']:
                discarded += 1
    return discarded, visited_once


        

