import os
import csv
import json
import numpy as np

def generate_config(params):

    file_name = "configs/" + str(params["n_stations"]) + "_stations_" + str(params["transition_procedure"]) + ".json"
    config_dict = {"STATION_COUNT": params["n_stations"],
                    "STATION_PROBS": params["transitions"],
                    "SHUFFLE_STATIONS": False,
                    "MAINTENANCE_INTERVAL": 3600,
                    "SIM_DURATION": 864000,
                    "ORDER_FREQUENCY": 0.00166667,
                    "ORDER_PRIORITIES": 5}
    
    with open(file_name, "w") as outfile: 
        json.dump(config_dict, outfile)

def calc_transitions(params):

    n_stations = params["n_stations"]
    transition_procedure = params["transition_procedure"]
    
    if "percentage" in params.keys():
        percentage = params["percentage"]

    if "corridor_width_left" in params.keys():
        corridor_width_left = params["corridor_width_left"]
        corridor_width_right = params["corridor_width_right"]

    if transition_procedure=="READ":

        transitions = []
        with open(os.getcwd() + '/configs/' + transition_file, newline='') as csvfile:

            transitions_reader = csv.reader(csvfile, delimiter=';')

            for row in transitions_reader:
                
                row = [float(e) for e in row]
                transitions.append(row)
                
    elif transition_procedure=="UNIFORM":

        transitions = np.ones((n_stations, n_stations))
        transitions = transitions/n_stations

        transitions = [[element for element in elements] for elements in transitions]
    
    elif transition_procedure=="UNIFORM_UPPER_TRIANGLE":

        transitions = np.triu(np.ones((n_stations, n_stations)), 1)
        transitions[n_stations-1, n_stations-1] = 1
        transitions = transitions/transitions.sum(axis=1, keepdims=True)

        transitions = [[element for element in elements] for elements in transitions]

    elif transition_procedure=="UNIFORM_CORRIDOR":
        
        transitions = np.ones((n_stations, n_stations))
        keep_matrix_upper = np.triu(np.ones((n_stations, n_stations)), -corridor_width_left)
        keep_matrix_lower = np.tril(np.ones((n_stations, n_stations)), corridor_width_right)
        keep_matrix = (keep_matrix_upper == 1) & (keep_matrix_lower == 1)
        transitions = np.where(keep_matrix==1, transitions, 0)
        transitions = transitions / transitions.sum(axis=1, keepdims=True)

        if np.isnan(transitions[n_stations-1, n_stations-1]):
            transitions[n_stations-1, :] = np.array([0 for i in range(0,n_stations-1)] + [1])

        transitions = [[element for element in elements] for elements in transitions]

        transition_procedure = transition_procedure + "_" + str(corridor_width_left) + "_" + str(corridor_width_right)

    elif transition_procedure=="UNIFORM_PERCENTAGE":
        
        transitions = np.ones(n_stations*n_stations)
        transitions[:int(((n_stations*n_stations)*(1-percentage)))] = 0
        np.random.shuffle(transitions)
        transitions.shape = (n_stations, n_stations)
        transitions = transitions / transitions.sum(axis=1, keepdims=True)

        for row in range(0, len(transitions)):
            if np.isnan(transitions[row, n_stations-1]):
                shuffle_transitions = np.array([0 for i in range(0,n_stations-1)] + [1])
                np.random.shuffle(shuffle_transitions)
                transitions[row, :] = shuffle_transitions

        transitions = [[element for element in elements] for elements in transitions]

        transition_procedure = transition_procedure + "_0" + str(percentage).split(".")[1]

    elif transition_procedure=="RANDOM":

        transitions = np.random.rand(n_stations, n_stations)
        transitions = transitions / transitions.sum(axis=1, keepdims=True)

        transitions = [[element for element in elements] for elements in transitions]

    elif transition_procedure=="RANDOM_CORRIDOR":

        transitions = np.random.rand(n_stations, n_stations)
        keep_matrix_upper = np.triu(np.ones((n_stations, n_stations)), -corridor_width_left)
        keep_matrix_lower = np.tril(np.ones((n_stations, n_stations)), corridor_width_right)
        keep_matrix = (keep_matrix_upper == 1) & (keep_matrix_lower == 1)
        transitions = np.where(keep_matrix==1, transitions, 0)
        transitions = transitions / transitions.sum(axis=1, keepdims=True)

        if np.isnan(transitions[n_stations-1, n_stations-1]):
            transitions[n_stations-1, :] = np.array([0 for i in range(0,n_stations-1)] + [1])

        transitions = [[element for element in elements] for elements in transitions]

        transition_procedure = transition_procedure + "_" + str(corridor_width_left) + "_" + str(corridor_width_right)

    elif transition_procedure=="RANDOM_UPPER_TRIANGLE":
    
        transitions = np.triu(np.random.rand(n_stations, n_stations), 1)
        transitions[n_stations-1, n_stations-1] = 1
        transitions = transitions/transitions.sum(axis=1, keepdims=True)

        transitions = [[element for element in elements] for elements in transitions]

    elif transition_procedure=="RANDOM_PERCENTAGE":
        
        transitions = np.random.rand(n_stations*n_stations)
        transitions[:int(((n_stations*n_stations)*(1-percentage)))] = 0
        np.random.shuffle(transitions)
        transitions.shape = (n_stations, n_stations)
        transitions = transitions / transitions.sum(axis=1, keepdims=True)

        for row in range(0, len(transitions)):
            if np.isnan(transitions[row, n_stations-1]):
                shuffle_transitions = np.array([0 for i in range(0,n_stations-1)] + [1])
                np.random.shuffle(shuffle_transitions)
                transitions[row, :] = shuffle_transitions

        transitions = [[element for element in elements] for elements in transitions]

        transition_procedure = transition_procedure + "_0" + str(percentage).split(".")[1]

    return(transitions, transition_procedure)
    
if __name__ == "__main__":

    # transition_file = "transitions_10_stations_self_loops.csv"

    n_stations_values = [5, 10, 20, 40, 80, 150, 250, 500]
    percentage_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    corridor_width_right_values = [3, 2, 1]
    corridor_width_left_values = [-1]
    transition_procedure_values = ["UNIFORM_UPPER_TRIANGLE", "UNIFORM_CORRIDOR", "RANDOM_UPPER_TRIANGLE", "RANDOM_CORRIDOR", "RANDOM_PERCENTAGE"]

    base_combinations = [{"n_stations":a, "transition_procedure":b} for a in n_stations_values for b in transition_procedure_values if b in ["UNIFORM", "UNIFORM_UPPER_TRIANGLE", "RANDOM", "RANDOM_UPPER_TRIANGLE"]]
    corridor_combinations = [{"n_stations":a, "transition_procedure":b, "corridor_width_right":c, "corridor_width_left":d} for a in n_stations_values for b in transition_procedure_values if b in ["UNIFORM_CORRIDOR", "RANDOM_CORRIDOR"] for c in corridor_width_right_values for d in corridor_width_left_values]
    percentage_combinations = [{"n_stations":a, "transition_procedure":b, "percentage":c} for a in n_stations_values for b in transition_procedure_values if b in ["UNIFORM_PERCENTAGE", "RANDOM_PERCENTAGE"] for c in percentage_values]

    all_combinations = base_combinations + corridor_combinations + percentage_combinations

    for transition_params in all_combinations:
    
        transitions, transition_procedure = calc_transitions(transition_params)

        config_params={"n_stations":transition_params["n_stations"], "transition_procedure":transition_procedure, "transitions":transitions}

        generate_config(config_params)