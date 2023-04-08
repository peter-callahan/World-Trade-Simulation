# World Trade Simulation

## Getting Started

1. Ensure you have the contents of requirements.txt in your environment or virtual environment. 
2. Python version 3.10.6 was used to create this simulation, but it should work with anything >= 3.7.

## Config Files

* initial_world_state.csv - states countries in play and resources allocated to each at beginning of simulation.
* resource_weight.csv - assigns value "weights" to resources which are used in calculating the utility of each country in the simulation.
* templates.json - a list of creation events each country may perform, this is a JSON version of the templates supplied in the project overview.  

## Config Settings

Settings may be adjusted from inside the tradesim.py script.  They are marked in the top 40 lines of code and include descriptions. 

## How to run 

Set your configuration parameters in tradesim.py and run the tradesim.py command.  Note that the script will look for the config files listed above in the same directory that you run the script.  You can adjust this using the base_dir variable inside the tradesim.py file, but if you run everything in the same 
directory it will work fine. 

## Output

This agent uses an anytime serach and will return the a better search strategy if it encounters it.  When this occurs the following files get updated:

1. best_node_transaction_list.txt - a list of transactions starting with the initial state.
2. best_node_metadata.txt - relevant metadata related to the search, like final global utility (of best search) and other relevant metadata
3. best_node_network_graph.json - a list of items representing a network graph of the portion of the tree searched when the new best search was discovered.  This is more than a list of transactions but represents a directed graph representing all the nodes visited during the search.  

