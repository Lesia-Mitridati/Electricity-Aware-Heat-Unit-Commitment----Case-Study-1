# Electricity-Aware-Heat-Unit-Commitment----Case-Study-1
case study 1 in the companion paper, representing the modified IEEE 24-bus system and 2 isolated 3-node district heating networks. 

input_gen_data.csv: includes all techno-economic parameters of heat and electricity generators
input_load_data.csv: includes all techno-economic parameters of heat and electricity loads
input_time_series.csv: includes all time series for loads, and renewable production
input_system_data.csv: includes all system parameters

initialize.py: loads data into a dictionary and initialized the results for 3 models (integrated, hierarchical, and decoupled) in a dictionary
