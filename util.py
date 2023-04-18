from collections.abc import Mapping
import math
import csv

## Utility Functions
def flatten_list(l):
    return [item for sublist in l for item in sublist]
    
# https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
def update_dict(d, update_dict):

    for k, v in update_dict.items():

        if isinstance(v, Mapping):
            d[k] = update_dict(d.get(k, {}), v)
        
        else:
            d[k] = v
    
    return d

def get_turn_tracker(depth, counties):

    if depth < len(counties):
        raise ValueError('Pick a new depth value, need to have at least as much depth as number of countries.')

    counter = 1

    turn_tracker = dict()

    round_up = math.ceil(depth / len(counties))

    for x in range(1, round_up + 1):

        for y, country in enumerate(counties):

            turn_tracker[counter] = country
            counter = counter + 1

    return turn_tracker

def initialize_transaction_sequence(filename, headers):
    '''
    filename: name of log file for current run
    headers: column names to be logged, must match what is recorded during simulation run
    '''
    with open(filename, 'w') as f:    
        wr = csv.writer(f)
        wr.writerow(headers)
 