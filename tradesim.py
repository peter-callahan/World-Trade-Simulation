
import json
import os
import csv

from country import Country
from datetime import datetime
from simulation_node import Simulation_Node, Simulation_Orchestrator
from util import get_turn_tracker, initialize_transaction_sequence
from config.simulation_configuration import (
    countries,
    my_country_name,
    total_counter,
    config_location
)

from copy import copy
from tqdm import tqdm # for progress bar

# Initialize Conditions and Build Countries

init_state_data = os.path.join(config_location, 'initial_world_state.csv')
init_resource_weights = os.path.join(config_location, 'resource_weight.csv')
templates = os.path.join(config_location, 'templates.json')

with open(templates, 'r') as f:
    template_dict = json.load(f)

other_countries = [x for x in countries if x != my_country_name]

world_list = {}
frontier = dict()

verbose = False

orchestrator = Simulation_Orchestrator(countries)

# Create player 1 country
my_country = Country(my_country_name,
                    init_state_data=init_state_data,
                    init_resource_weights=init_resource_weights,
                    templates=templates)

world_list[my_country.name] = my_country

# Add other countries
for country in other_countries:

    next_country = Country(country,
                        init_state_data=init_state_data,
                        init_resource_weights=init_resource_weights,
                        templates=templates)

    world_list[next_country.name] = next_country


turn_tracker_input = get_turn_tracker(orchestrator.max_depth, countries)

first_node = Simulation_Node(world_list, turn_tracker=turn_tracker_input)

_ = first_node.get_options(minimum_transfer=orchestrator.minimum_transfer,
                        intervals_to_check=orchestrator.create_intervals,
                        sort_method=orchestrator.sort_strategy,
                        frontier=frontier,
                        max_repeats=orchestrator.max_repeats)

del world_list          # don't use it again, only interact with the model from here on out
del country
del next_country

# Take first step in the model

next_node, frontier = first_node.next_node_state(frontier)

next_node.parent_node = first_node
__ = next_node.get_options(minimum_transfer=orchestrator.minimum_transfer,
                        intervals_to_check=orchestrator.create_intervals,
                        frontier=frontier,
                        sort_method=orchestrator.sort_strategy,
                        max_repeats=orchestrator.max_repeats)

best_node_so_far = copy(next_node)
best_node_so_far.parent_node = first_node

best_actions = []
node_explore = 0

new_best_score_alert = True

pbar = tqdm(total=total_counter)

verbose = False

utility_tracker = []

saved_timestamp = datetime.now().strftime("%Y-%m-%d %H_%M_%S")
model_log_filename = f'./sim_runs/{saved_timestamp}_best_node_transaction_list.csv'
initialize_transaction_sequence(filename=model_log_filename, headers=['Model_ID', 'Global_Utility', 'Depth','Action_Type', 'Actor', 'Target', 'Action', 'Quantity'])

# Enter simulation sequence

while total_counter > 0:

    total_counter = total_counter - 1

    utility_tracker.append(
        (next_node.global_utility, next_node.depth, total_counter)
        )

    if total_counter % 10 == 0:
        pbar.update(10)

    if total_counter % 1000 == 0:  # append list of transactions for most recent node to a list so we can snapshot where we are in the search
        pass

    if next_node is None:     # Back at root note with nowhere else to go, exit.
        break

    elif next_node.depth == orchestrator.max_depth: # reached depth limit, proceed to prev node
        next_node = next_node.prev_node_state(verbose=verbose)

    else:
        __ = next_node.get_options(
            minimum_transfer=orchestrator.minimum_transfer,
            intervals_to_check=orchestrator.create_intervals,
            frontier=frontier,
            sort_method=orchestrator.sort_strategy,
            max_repeats=orchestrator.max_depth
            )

        # no actions for this player at this node
        if len(next_node.possible_actions[ next_node.country_acting ]) == 0:

            # back at root node and out of options, end!
            if next_node.depth == 1:
                break

            next_node = next_node.prev_node_state(verbose=verbose)

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

                    metadata_filename = f'./sim_runs/{saved_timestamp}_best_node_metadata.txt'

                    with open(metadata_filename, 'w') as f:

                        output = (f"Final Global Utility {best_node_so_far.global_utility}\n"
                                f"Utility Delta (from Initial State): {best_node_so_far.global_utility - first_node.global_utility}\n"
                                f"Max Depth: {orchestrator.max_depth}\n"
                                f"Sort Strategy: {orchestrator.sort_strategy}\n"
                                )

                        f.write(str(output))

                    _ = best_node_so_far.extract_transaction_sequence(filename=model_log_filename)

pbar.close()

# export log of global utility changes for graphing

node_filename = f'./sim_runs/{saved_timestamp}_node_log.csv'
with open(node_filename, 'w') as f:

    wr = csv.writer(f)
    wr.writerow(['step', 'global_util', 'depth', 'count_remaining'])

    for n, log in enumerate(utility_tracker):
        wr.writerow([n, *log])


