import secrets
import csv

from copy import deepcopy
from collections import Counter
from random import shuffle, randrange
from math import floor

from config.simulation_configuration import (
    MINIMUM_TRANSFER,
    CREATE_INTERVALS,
    SORT_STRATEGY,
    MAX_DEPTH,
    MAX_REPEATS,
    )


class Simulation_Orchestrator(object):

    minimum_transfer = MINIMUM_TRANSFER
    create_intervals = CREATE_INTERVALS
    sort_strategy = SORT_STRATEGY
    max_depth = MAX_DEPTH
    max_repeats = MAX_REPEATS
    global_utlilty = -1
    current_node_utilities = dict()

    def __init__(self, country_list):
        self.country_list = country_list

    # provide seperation of concerns between indivitual Simulation Nodes (runs) and the Simulation World (orchestrator, tracker)

    # track world level metrics here - best run and highest utility

    # total steps in search tree


class Simulation_Node(Simulation_Orchestrator):

    def __init__(self, country_list, turn_tracker, parent_node=None, depth=1, global_utility=-1, possible_actions=dict(), action_taken=''):
        # store countries and resources in global simulation
        self.country_dict = country_list
        self.global_utility = global_utility

        self.hex_name = secrets.token_hex(nbytes=16)
        self.possible_actions = possible_actions  # possible actions apply to the country level, updated on each step of model
        self.action_taken = action_taken          # actions taken at a specific node
        self.parent_node = parent_node
        self.turn_tracker = turn_tracker
        self.country_acting = self.turn_tracker[depth]
        self.depth = depth

        super().__init__(country_list)

    def __repr__(self):

        return f'''
        {type(self).__name__}(
            Country Acting={self.country_acting}
            Global Utility={self.global_utility}
            Parent Node={self.parent_node}
            )
            '''


    def get_discount_rate(self):
        '''Discounts returns based on depth level: more trades == higher depth == higher discount'''
        multiple = max(self.turn_tracker.keys()) // 3

        if self.depth <= 1 * multiple:
            return 1

        elif self.depth <= 2 * multiple:
            return 0.9

        else:
            return 0.8

    def track_previously_performed_events(self, parent_node_id, event, frontier):

        if parent_node_id in frontier.keys():

            # check if event occurred at a given parent node N
            if event in frontier[parent_node_id]:
                frontier[parent_node_id][event] += 1
            else:
                frontier[parent_node_id][event] = 1

        # new parent node, add it to the tracker
        else:
            frontier[parent_node_id] = { event : 1 }

    def update_country_states(self, country_to_update):
        '''
        Update Country object inside the current Simulation Node.
        Necesarry to perform this update as countries change resources.
        '''
        self.country_dict[country_to_update.name] = country_to_update

    def transfer(self, source_country, target_country, resource, amount_transferred, verbose=False, shadow_mode=False):

        if shadow_mode:
            # return event with util column added without changing self
            shadow_copy_source_country = deepcopy(self.country_dict[source_country])
            shadow_copy_target_country = deepcopy(self.country_dict[target_country])

            shadow_copy_source_country - {resource:amount_transferred}
            shadow_copy_target_country + {resource:amount_transferred}

            discount = self.get_discount_rate()

            shadow_copy_source_country.update_util(discount=discount)
            shadow_copy_target_country.update_util(discount=discount)

            net_util_benefit = shadow_copy_target_country.current_utility - shadow_copy_source_country.current_utility

            event = ('Transfer', source_country, target_country, resource, amount_transferred, net_util_benefit)
            return event

        else:
            # perform transaction
            self.country_dict[source_country] - {resource:amount_transferred}
            self.country_dict[target_country] + {resource:amount_transferred}

            event = ('Transfer', source_country, target_country, resource, amount_transferred)
            self.action_taken = event

            if verbose:
                print(event)

            return event

    def transform(self, country, template, qty = 1, verbose=False, shadow_mode=False):
        '''
        Transforms resources to new things using existing resources of the country object.
        Function check_resources ensures sufficient resources exist, this carries out transforms which we know we can perform.
        :param template: tranform template i.e. "CreateAlloy"
        :return: None
        '''
        to_expend = {}
        to_create = {}

        # self.country_dict[country] is a Country object not a pure dict, has some limitations
        for resource in self.country_dict[country].templates[template]['Inputs'].keys():   # resource_input == water, population, etc.

            # safety catch, this should never happen
            if self.country_dict[country].templates[template]['Inputs'][resource] * qty > self.country_dict[country].resources[resource]:

                raise ValueError(f'''Illegal Operation, cannot create {resource}, insufficient resources.  Resource check malfunction.
                    Needed {self.country_dict[country].templates[template]['Inputs'][resource] * qty} but only {self.country_dict[country].resources[resource]}''')

            to_expend[resource] = self.country_dict[country].templates[template]['Inputs'][resource] * qty

        for resource in self.country_dict[country].templates[template]['Outputs'].keys():
            to_create[resource] = self.country_dict[country].templates[template]['Outputs'][resource] * qty


        x = Counter(to_create)
        y = Counter(to_expend)

        y.subtract(x)

        if verbose:
            print(event)

        if shadow_mode:
            # don't change self
            shadow_copy_country = deepcopy(self.country_dict[country])

            shadow_copy_country - to_expend
            shadow_copy_country + to_create

            discount = self.get_discount_rate()

            shadow_copy_country.update_util(discount=discount)

            event = ('Create', country, country, template, qty, shadow_copy_country.current_utility)

            return event


        # subtract expended from resources
        self.country_dict[country] - to_expend

        # add output to resources
        self.country_dict[country] + to_create

        discount = self.get_discount_rate()

        self.country_dict[country].update_util(discount=discount)

        event = ('Create', country, country, template, qty)
        self.action_taken = event

        return event


    def update_global_expected_utiliziation(self, verbose=False):
        '''
        Calculates and returns global utilization by taking the average of all current utilities
        '''
        values = []

        for country in self.country_dict.keys():
            values.append(self.country_dict[country].current_utility)

        global_utility = sum(values) / len(values)

        if verbose:
            print(f"Global Utility: {global_utility}")

        self.global_utility = global_utility


    def calculate_utilization_of_options(self, options_list):

        output_list = []

        for option in options_list:

            if option[0] == 'Create':
                outcome = self.transform(option[1],
                                         template=option[3],
                                         qty=option[4],
                                         shadow_mode=True)

            elif option[0] == 'Transfer':
                outcome = self.transfer(source_country=option[1],
                                         target_country=option[2],
                                         resource=option[3],
                                         amount_transferred=option[4],
                                         shadow_mode=True)

            else:
                raise ValueError('Unknown command in option list')

            output_list.append(outcome)

        return output_list


    def get_options(self, minimum_transfer, intervals_to_check, frontier, sort_method='std', max_repeats=3, reduction_limit=0.9):
        # Options recalculated at each node, for each acting country, based on changing resources.

        if self.parent_node is None:
            parent_identifier = 'top_level_node'

        else:
            parent_identifier = self.parent_node.hex_name

        options =  self.country_dict[self.country_acting].generate_country_options(self.country_dict.keys(),
                                                        parent_node_id=parent_identifier,
                                                        frontier=frontier,
                                                        minimum_transfer=minimum_transfer,
                                                        intervals_to_check=intervals_to_check,
                                                        max_repeats=max_repeats)

        # price out all options, apply sorting method here!
        options_with_util = self.calculate_utilization_of_options(options)

        if sort_method == 'std':
            sorted_options = options_with_util

        elif sort_method == 'create_first':
            sorted_options = sorted(options_with_util, key=lambda x: x[0], reverse=False)

        elif sort_method == 'transfer_first':
            sorted_options = sorted(options_with_util, key=lambda x: x[0], reverse=True)

        elif sort_method == 'utility_first':
            sorted_options = sorted(options_with_util, key=lambda x: x[5], reverse=True)

        elif sort_method == 'utility_first_and_reduce':
            sorted_options = sorted(options_with_util, key=lambda x: x[5], reverse=True)

            reduction_limit = floor(len(sorted_options) * reduction_limit)

            # if down to 3 options, do not remove anything
            if reduction_limit > 3:

                for x in range(0, reduction_limit):
                    sorted_options.pop(randrange(len(sorted_options)))


        elif sort_method == 'utility_last':
            sorted_options = sorted(options_with_util, key=lambda x: x[5], reverse=False)

        elif sort_method == 'random':
            shuffle(options_with_util)
            sorted_options = options_with_util

        elif sort_method == 'random_and_reduce':

            # remove ~20% of list elements randomly
            reduction_limit = floor(len(options_with_util) * reduction_limit)

            # if down to 3 options, do not remove anything
            if reduction_limit > 3:

                for x in range(0, reduction_limit):
                    options_with_util.pop(randrange(len(options_with_util)))

            shuffle(options_with_util)
            sorted_options = options_with_util

        else:
            raise ValueError('Invalid sort method.')

        self.possible_actions[self.country_acting] = sorted_options

        return options

    def prev_node_state(self, verbose=False, log_no_action=False):
        '''
        return node that is one node up on the graph
        '''

        prev_node = deepcopy(self.parent_node)

        if log_no_action and verbose:
            print(f'{self.depth} {self.country_acting} No action, up one node.')

        # things from self are preserved as we move upward to a parent node.  We need to roll back depth and parent.parent to keep history.
        # self.country_dict contains history, need to keep track to apply logic based on what we've done so far.
        return self.__class__(
            prev_node.country_dict,
            parent_node=prev_node.parent_node,
            global_utility=prev_node.global_utility,
            turn_tracker=prev_node.turn_tracker,
            possible_actions=prev_node.possible_actions,
            action_taken=prev_node.action_taken,               # roll back everything expect actions taken.
            depth=prev_node.depth
            )

    def next_node_state(self, frontier, verbose=False, minimum_transfer=[200], intervals_to_check=[100,10]):

        country = self.country_acting

        for next_move in self.possible_actions[country]:
            #  What,        From,      To,          Material,      Amount
            # ('Create',   'Atlantis', 'Atlantis', 'CreateAlloys', 1)
            # ('Transfer', 'Atlantis', 'Carpania', 'Water',        100)

            if next_move[0] == 'Create':
                outcome = self.transform(self.country_dict[country].name, template = next_move[3], qty = next_move[4], verbose=verbose)

                self.update_global_expected_utiliziation()
                self.update_country_states(self.country_dict[country])

            elif next_move[0] == 'Transfer':
                outcome = self.transfer(self.country_dict[country].name, next_move[2], next_move[3], next_move[4], verbose=verbose)

                self.update_global_expected_utiliziation()
                self.update_country_states(self.country_dict[country])
                self.update_country_states(self.country_dict[next_move[2]])

            else:
                raise ValueError("Illegal Transformation Detected.")

            if self.parent_node is None:
                parent_identifier = 'top_level_node'

            else:
                parent_identifier = self.parent_node.hex_name

            self.track_previously_performed_events(parent_identifier, outcome, frontier)
            self.possible_actions[country].remove(next_move)

            if verbose:
                print(f'{self.depth} {self.country_acting} {outcome}')

            # only single action takend off possible_actions
            break

        # https://stackoverflow.com/questions/4996565/idiomatic-python-for-generating-a-new-object-from-within-a-class
        return (self.__class__(self.country_dict,
            # history=self.history,
            parent_node=self.parent_node,
            global_utility=self.global_utility,
            turn_tracker=self.turn_tracker,
            possible_actions=self.possible_actions,
            action_taken=self.action_taken,
            depth=self.depth + 1),
            frontier)

    def extract_transaction_sequence(self, filename=None):

        # do not change self, perform calculation and step through on a copy of self
        starting_node = deepcopy(self)

        # ensures a unique node name for telling model data apart from one another
        salt = str(secrets.randbelow(500000)).zfill(6)

        transactions = []

        while starting_node.parent_node is not None:

            transactions.append(starting_node.action_taken)
            starting_node = starting_node.prev_node_state()

        # include the first transaction.  We are backing out of the tree so the first transaction gets recorded last.
        transactions.append(starting_node.action_taken)

        list_output = list(reversed(transactions))

        if filename:
            with open(filename, 'a') as f:

                wr = csv.writer(f)
                for row in list_output:
                    wr.writerow([(self.hex_name + '_' + salt), self.global_utility, self.depth, *row])

        return list_output
