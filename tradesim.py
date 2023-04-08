
import json
import os
import sys

from country import Country
from simulation_node import Simulation_Node
from util import get_turn_tracker
from simulation_configuration import MINIMUM_TRANSFER, CREATE_INTERVALS, SORT_STRATEGY, MAX_DEPTH, MAX_REPEATS, countries, my_country_name, total_counter, base_dir

from copy import copy
from tqdm import tqdm # for progress bar

# Initialize Conditions and Build Countries 

init_state_data = os.path.join(base_dir, 'initial_world_state.csv')
init_resource_weights = os.path.join(base_dir, 'resource_weight.csv')
templates = os.path.join(base_dir, 'templates.json')

with open(templates, 'r') as f: 
    template_dict = json.load(f)

other_countries = [x for x in countries if x != my_country_name]

world_list = {}
frontier = dict()

verbose = False

my_country = Country(my_country_name, 
                    init_state_data=init_state_data, 
                    init_resource_weights=init_resource_weights, 
                    templates=templates)

world_list[my_country.name] = my_country

for country in other_countries:
    next_country = Country(country,
                        init_state_data=init_state_data,
                        init_resource_weights=init_resource_weights,
                        templates=templates)

    world_list[next_country.name] = next_country


turn_tracker_input = get_turn_tracker(MAX_DEPTH, countries)

first_node = Simulation_Node(world_list, turn_tracker=turn_tracker_input)

_ = first_node.get_options(minimum_transfer=MINIMUM_TRANSFER, 
                           intervals_to_check=CREATE_INTERVALS, 
                           sort_method=SORT_STRATEGY,
                           frontier=frontier,
                           max_repeats=MAX_REPEATS)

#global_hist = []
#global_hist.append(first_node)

del world_list          # don't use it again, only interact with the model from here on out
del country
del next_country

next_node, frontier = first_node.next_node_state(frontier)
next_node.parent_node = first_node
__ = next_node.get_options(minimum_transfer=MINIMUM_TRANSFER, 
                           intervals_to_check=CREATE_INTERVALS, 
                           frontier=frontier,
                           sort_method=SORT_STRATEGY,
                           max_repeats=MAX_REPEATS)

#global_hist.append(next_node)

best_node_so_far = copy(next_node)
best_node_so_far.parent_node = first_node

# no_actions = []
best_actions = []
node_explore = 0

new_best_score_alert = True

pbar = tqdm(total=total_counter)

verbose = False

while total_counter > 0:

    total_counter = total_counter - 1

    if total_counter % 10 == 0:
        pbar.update(10)
        #print( sys.getsizeof(next_node) )

    # we are back at root with nowhere to go.  End.
    if next_node is None:
        break

    # hit depth limit or run out of options, go up one level
    elif next_node.depth == MAX_DEPTH:
        
        next_node = next_node.prev_node_state(verbose=verbose)
        #global_hist.append(next_node)

    else:
        __ = next_node.get_options(minimum_transfer=MINIMUM_TRANSFER, 
                                   intervals_to_check=CREATE_INTERVALS,
                                   frontier=frontier, 
                                   sort_method=SORT_STRATEGY,
                                   max_repeats=MAX_REPEATS)

        # no actions for this player at this node
        if len(next_node.possible_actions[ next_node.country_acting ]) == 0:

            #no_actions.append((next_node.country_acting, next_node.depth, next_node.parent_node))

            # back at root node and out of options, end!
            if next_node.depth == 1: 
                break

            next_node = next_node.prev_node_state(verbose=verbose)
            #global_hist.append(next_node)

        # proceed with selecting an action, advance down decision tree
        else:
            prev_node = copy(next_node)

            next_node, frontier = prev_node.next_node_state(frontier, verbose=verbose)
            next_node.parent_node = prev_node
            #global_hist.append(next_node)
            del prev_node

            # only eval "best node" for new nodes, if we are backing out no need to check!
            if next_node.depth > 1:

                # need to return these for anytime search
                if best_node_so_far.global_utility < next_node.global_utility:
                    
                    best_node_so_far = copy(next_node)
                    best_node_so_far.parent_node = next_node

                    best_node_data = (best_node_so_far.global_utility, best_node_so_far.depth, best_node_so_far)

                    if new_best_score_alert:
                        print(f'New best score! {best_node_data[:2]}')

                    best_actions.append(best_node_data)

                    #with open('best_node_network_graph.json', 'w') as f:
                    #    json.dump(best_node_so_far.history, f, indent=4)

                    with open('best_node_metadata.txt', 'w') as f:

                        output = (f"Final Global Utility {best_node_so_far.global_utility}\n"
                                  f"Utility Delta (from Initial State): {best_node_so_far.global_utility - first_node.global_utility}\n"
                                  f"Max Depth: {MAX_DEPTH}\n"
                                  f"Sort Strategy: {SORT_STRATEGY}\n"
                                 )
                        
                        f.write(str(output))
                    
                    transactions_of_best_outcome = best_node_so_far.extract_transaction_sequence() 

                    with open('best_node_transaction_list.txt', 'w') as f:
                        for transaction in transactions_of_best_outcome:
                            f.write(str(transaction) + "\n")

pbar.close()

