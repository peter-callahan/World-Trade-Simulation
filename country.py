import json
import pandas as pd

class Country:
    '''
    country_name: path to CSV containing state data
    init_state_data: path to CSV file containing state data
    init_resource_weights: path to CSV file containing resource weight data
    templates = 'templates.json': path to JSON object that represents templates (blueprints)
    '''
    
    def __init__(self, country_name: str, init_state_data: str, init_resource_weights: str, templates: str = 'templates.json'):

        self.name = country_name

        world_state = self.csv_to_json_parser(init_state_data, orient='index')
        self.resources = world_state[country_name]

        weights = self.csv_to_json_parser(init_resource_weights, orient='columns')

        self.resource_weights = weights['Weight']
        self.resource_transferable = weights['Transferable']
        self.country_frontier = dict()

        # if we encouter resources that do not have defined weights/transferaility, assume weight 0 and not transferable. 
        for resource in self.resources:
            if resource not in self.resource_transferable:
                self.resource_transferable[resource] = False
            if resource not in self.resource_weights:
                self.resource_weights[resource] = 0

        with open(templates) as input_file:
            x = json.loads(input_file.read())
            self.templates = x

        self.current_utility = 0
        self.update_util(util_init=True)

    def __repr__(self):
        return f'''
        {type(self).__name__}(
            Name={self.name}
            Resource Weights={self.resource_weights}, 
            Resource Transferable={self.resource_transferable},
            Resources={self.resources}
            Templates={self.templates.keys()}
            )
            '''

    def __add__(self, transform_input: dict):
        '''
        takes in dictionary (input/output level from JSON) and adds values to current country
        :param transform_input:
        :return:
        '''

        for resource in transform_input.keys():
            if resource in self.resources:  
                self.resources[resource] = self.resources[resource] + transform_input[resource]
            else:
                self.resources[resource] = transform_input[resource]

    def __sub__(self, transform_input:dict):
        # takes in dictionary and removes values from current country
        # check to be performed outside this function call
        
        # only log subtractions (transfers) and transforms, "received from" is reduntant

        for resource in transform_input.keys():
            self.resources[resource] = self.resources[resource] - transform_input[resource]


    def update_util(self, util_init=False, verbose=False, discount=1):

        temp_util = 0

        for k, v in self.resources.items():

            if k not in self.resource_weights.keys():
                #todo consider handling this differently, right now we will ignore from calculation
                pass
                # raise ValueError(f'Missing key {k} from resource weight table.')
            else:
                temp_util = temp_util + (v * self.resource_weights[k])

        temp_util = (temp_util / self.resources['Population']) * discount

        if not util_init and verbose:
            print(f'[{self.name}] Utility updated {self.current_utility} -> {temp_util}')
            
        self.current_utility = temp_util

    # Evaluate one move ahead, calculating the expected utility of completing it
    def expected_util(selp):
        pass

    def check_resources(self, create_action:str, multiplier:int):
        '''
        ensure the transform can be completed with existing resources
        :param create_action: the name (str) of the thing to be created (i.e. CreateHousing)
        :return: Tuple 
            True/False, indicating the presence or absense of sufficient resources
            Multiplier, an integar indicating the quantity of an item to be created.  If the test passes, this is the amount be can make.
            List of Tuples indicating resource shortages that caused the check to fail
        '''

        test_pass = True
        insufficient_resources = []

        necessary_input_resources = self.templates[create_action]['Inputs'].keys()

        for resource in necessary_input_resources:
            
            cost_to_build = self.templates[create_action]['Inputs'][resource] * multiplier
            current_resource = self.resources[resource]
            
            if resource in self.resources:
                if current_resource < cost_to_build:
                    shortage = current_resource - cost_to_build
                    insufficient_resources.append((resource, shortage))
                    test_pass = False
                
                if current_resource >= cost_to_build:
                    shortage = 0

            elif resource not in self.resources:
                shortage = -cost_to_build
                insufficient_resources.append((resource, shortage))
                test_pass = False

            else:
                raise ValueError("Unexpected logic encountered, this should never happen. lLkKodZdhk")

        return (test_pass, multiplier, insufficient_resources)

    def csv_to_json_parser(self, csv_data, orient):

        csv_data = pd.read_csv(csv_data, index_col=[0])
        
        return json.loads(csv_data.to_json(orient=orient, indent=4))

    def generate_country_options(self, world_list, parent_node_id, frontier, minimum_transfer=[200], intervals_to_check=[100,10], max_repeats=3):
        
        options = []

        for next_template in self.templates.keys():
            
            for multiplier in intervals_to_check:

                resources_exist, qty_to_make, resource_shortage = self.check_resources(next_template, multiplier)

                if resources_exist:

                    new_option = ('Create', self.name, self.name, next_template, qty_to_make)
                    seen_before = frontier.get(parent_node_id, {}).get(new_option, 0)
                    # seen_before = self.country_frontier.get(parent_node_id, {}).get(new_option, 0)
                    # seen_before = self.country_frontier.get(current_depth, {}).get(new_option, 0)

                    if seen_before <= max_repeats:
                        options.append(new_option)

        # check for transfers
        for resource in self.resources.keys():

            for local_min in minimum_transfer:

                if self.resources[resource] >= local_min and self.resource_transferable.get(resource, False) is True:

                    for other_country in world_list:

                        if other_country == self.name:
                            # ensure transfers to self do not occur but transfers to other countries are considered.
                            pass 
                        else:
                            # max_resources = country.resources[resource]
                            # options.append((resource, max_resources))

                            new_option = ('Transfer', self.name, other_country, resource, local_min)
                            seen_before = frontier.get(parent_node_id, {}).get(new_option, 0)
                            # seen_before = self.country_frontier.get(parent_node_id, {}).get(new_option, 0)
                            # seen_before = self.country_frontier.get(current_depth, {}).get(new_option, 0)

                            if seen_before < max_repeats:

                                options.append(new_option)

        return options 