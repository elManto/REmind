import configparser
import os


CURRENT = os.path.dirname(os.path.abspath(__file__))
#DB_CONFIG = '../sql/config.db'
GENERAL_CONFIG = './challs.ini'

config = configparser.ConfigParser()
config.read(os.path.join(CURRENT, GENERAL_CONFIG))
config_dictionary = dict()

config_dictionary['glance_static_interval'] = int(config['DEFAULT']['glance_static_interval'])
config_dictionary['max_time'] = int(config['DEFAULT']['max_time'])

def set_binary(challenge_id):
    key = 'binary{0}'.format(challenge_id) 
    assert (key in config)
    binary_dictionary = {
            'base' : int(config[key]['base']),
            'length' : int(config[key]['length']),
            'target_offsets' : [int(offs) for offs in config[key]['target_offsets'].split(',')],
            'functions' : config[key]['functions_to_analyse'].split(','),
            'path_to_json' : os.path.join(CURRENT, config[key]['path_to_json'])
            }

    config_dictionary['binary1'] = binary_dictionary
