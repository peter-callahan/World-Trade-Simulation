# World Trade Simulation

## Getting Started

1. Ensure you have the contents of requirements.txt in your environment or virtual environment. 
2. Python version 3.10.6 was used to create this simulation, but it should work with anything >= 3.7.

## Config Files

* initial_world_state.csv - states countries in play and resources allocated to each at beginning of simulation.
* resource_weight.csv - assigns value "weights" to resources which are used in calculating the utility of each country in the simulation.
* templates.json - a list of creation events each country may perform, this is a JSON version of the templates supplied in the project overview.  

## Config Settings

Settings may be adjusted from inside the simulation_configuration.py file.

## How to run 

### Run a single script
Set your configuration parameters and run tradesim.py.  Note that the script will look for the config files listed above in the same directory that you run the script.  You can adjust this using the base_dir variable inside simulation_configuration.py.  

### Run the script many times
Set your configuration parameters (see config settings above).  Then run the orchestrator.py file, which invokes the tradesim.py file and runs the model 25 times in a row.  If so inclined you could change the number of reruns by changing the value on line 21 of orchestrator.py. 

---

## Output

### Single Run
This agent uses an anytime search and will return a better search outcome anytime it encounters one.  When this occurs the following files get created and saved in the "sim_runs" folder.

1. {TIMESTAMP HH_MM_SS}_best_node_transaction_list.txt - a list of transactions starting with the initial state.
2. {TIMESTAMP HH_MM_SS}_best_node_metadata.csv - relevant metadata related to the search such as the final global utility (of the best search) and other relevant metadata
3. {TIMESTAMP HH_MM_SS}_node_log.csv - a list of the running global utility at every step during model run.  This is used to see when, during a specific simulation, the highest score was reached. 

---

## Findings

* [YouTube Discussion, Part 1](https://www.youtube.com/watch?v=1pSE9G9kXzU)
* [YouTube Discussion, Part 2](https://www.youtube.com/watch?v=hC5cQv9ajdo)

I found that my AI agent often became lost in the search space, due to the high branching factor and the increasing depth I wanted to explore.  For this reason I needed a way to find new areas of the search space I never encountered before. 

Initially, I hoped to find new areas of the search space by randomizing the action of each AI agent.  This method proved unreliable in isolation, I think there were too many bad options available at each decision point such that random selection resulted in mediocre outcomes which failed to unlock any new, high-value options. 

https://github.com/peter-callahan/trade_simulation/issues/4

The next option I explored was to reduce the branching factor of each node to explore higher search depths without losing the agent to an infinite search.  With my simulation higher search depth was essential.  Each agent modeled a country in the world trade simulation and acted in sequential order, so a world of 4 agents with a search depth of 12 meant every agent could choose 3 actions.  I felt getting deeper into the search tree would be the best way to make the simulation useful, because it would be able to find solutions several steps beyond what was visible at the outset.  

To reduce the search space I borrowed an idea discussed in lecture, randomly selecting a few actions from a larger group of potential actions.  This allowed my AI agent to consider fewer options which reduced the branching factor of the simulation significantly.  Those options which were randomly selected were already vetted through checks in my code, so they were valid.  The secondary benefit of this method was I could take an existing utility driven search and keep then "utility driven" property of it.  Instead of selecting options from a list at random I took the existing list of options, which was sorted by utility, and removed some percentage randomly (between 20% and 90%). This left me with a more compact list of options that was still sorted based on utility, across which the AI agent was to search.  This limited branching factor in a predictable way while still allowing me to maintain the utility first character of the search.  

This still resulted in random outcomes since options were eliminated at random.  This meant I had to be able to rerun the model multiple times over the same search space to mine for new areas of the search tree. To accomplish this I created a secondary script called orchestrator.py which called the primary model script multiple times.  The combination of reducing the branching factor randomly, maintaining a utility driven search, and implementing the orchestrator, allowed me to discover new areas of the search space which I had not previously found.  

With multiple model reruns being performed, I needed a better way to track and understand the simulations more deeply.  By improving the logging capability of the model I was able to compare numerous model reruns against each other.  

https://github.com/peter-callahan/trade_simulation/issues?q=is%3Aissue+is%3Aclosed

## Results
Test 1 and Test 2 - utility 5.26 to 5.58.
Added reduction and randomization of search options.  This is a mediocre score, not much improvement noted.  

Test 3 - utility 8.08
Maintained sort but reduced the search space (20%) and saw a significant improvement in model outcome.  

Test 4 - utility 7.04
Maintained sort, reduced search space (80%) and increased depth.  Found a good option but not as good as previous test case.  Note there is randomness at play in these runs as the search space is reduced in a random way. 

Test 5 - utility 5.34 - 6.66
Maintained sort, reduced search space (80%) and reduced iteration time.  There results were lackluster but illustrate the need for an auto-rerun capability when using the random search space reduction I have been pursuing.  

Test 6 - utility 9.2
Maintained sort, 80% search space reduction with reduced iteration and multiple reruns.  Reran the model 25 times sequentially resulting in 112 solutions of which this was the best. 

## Interesting Facts

Increasing depth generally had a positive effect on global utility, which makes sense intuitively since the agent has more changes to create value for itself.  But this was not always the case, some high depth solutions were not as good as a corresponding low-depth solution.  This can be seen in the figure below.

![Depth vs Utility](https://callpete-public.s3.amazonaws.com/world_trade_simulation/Depth+vs+Utility.png)

---

Some actions were more commonplace than others.  High depth solutions contained a higher percentage of transfer actions which may indicate the presence of trading loops in the agent. This would be an interesting area to explore further and search for ways to limit trades in an attempt to encourage unique solutions.  This activity may be driven by the utility function, which uses resource weights drive agent activity. 

![Distribution of Actions](https://callpete-public.s3.amazonaws.com/world_trade_simulation/Distribution+of+Actions.png)




