# update if running script from a file where configurations are not present (should not be necessary)
base_dir = './'

#################
# Configuration
#################



# Simulation config
# MINIMUM_TRANSFER = [200, 100, 50]           # multipliers to evaluate for possible transfers.  Default behavior: start high and go lower if resources are insufficint. 
MINIMUM_TRANSFER = list(range(200, 0, -50))
#CREATE_INTERVALS = [200, 100, 50]           # multipliers to evaluate for possible creations.  Default behavior: start high and go lower if resources are insufficint. 
CREATE_INTERVALS = list(range(200, 0, -50))
MAX_REPEATS = 1                             # model allows for repetition of actions at same country/depth state, but limits number of repeats to break loops 
MAX_DEPTH = 20                              

# Country config 
# Designate "your" country.  This will come with a custom configuration in Part2.
# List countries you want included in the simulation, these must appear in the initial_world_state.csv file.
my_country_name = 'Atlantis'
countries = ['Atlantis', 'Brobdingnag', 'Carpania', 'Dinotopia']   # 'Atlantis', 'Brobdingnag', 'Carpania', 'Dinotopia', 'Erewhon'

# Sort Strategy config 
# valid values: create_first, std, utility_first, utility_last, transfer_first
SORT_STRATEGY = 'utility_first'                

# used to limit number of steps taken in simulation.  Test with a low number then increase to set the upper bound. 
total_counter = 100

#################
## End of configuration
#################
   