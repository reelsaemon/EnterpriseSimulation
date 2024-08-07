# This is a simulation environment for generating enterprise data
# suitable for duration prediction purposes
# The data output after the simulation should form an event log
# with different activities/process steps that depend on some
# process variables that are modelled individually for each activity

#Todo
# - find a smart way to prioritize orders (otherwise low priority orders are in a deadlock if bottlenecks occur
#   and new orders with higher priorities are taking over)
#   maybe raise priority with waiting time or find another way to prioritize orders
#   planned duration generated at the beginning?
#   does the simulation need waiting pools for each station?
#   --> all orders have priority and time to deadline variables
#   --> sorting works by time to deadline first and then priority
#   --> order with longer tenure are picked first, priority is only second criterion
# - find a way to reset bottlenecks somehow
#   (not for configurations which are obviously always inducing bottlenecks, e.g. new order every second)
# - find a better functionality for the planned traces
#   stations via probabilities are not that smart
#   simulate traces per process model/petri net?
# - redesign workflow so that working speed depends on number of resources working on a case?
#   stations need individual resource pools?

import enterprise
import numpy as np
import pandas as pd
import json
import os
from datetime import datetime
from tqdm import tqdm


def simulate(sim_env):
    print("Simulating...")

    # simulation step
    for sim_step in tqdm(range(sim_env.timeManager.simDuration)):

        # simulate one iteration

        # # one order
        # if(sim_env.timeManager.simTime == 0):
        #     plan_probs = np.random.uniform(0, 1, len(sim_env.stations))
        #     current_station_plan = [sim_env.stations[i] for i in range(0, len(sim_env.stations)) if
        #                             plan_probs[i] <= sim_env.stationProbs[i]]
        #     sim_env.orderManager.generateOrder(np.random.choice(range(1, sim_env.orderManager.orderPriorities)),
        #                                        current_station_plan, sim_env.timeManager.simTime)

        # generate new orders
        # roll if order is to be generated this iteration
        # roll for order priority
        # include functionality for shuffling the planned stations (optional)
        if np.random.uniform() <= sim_env.orderManager.orderFrequency:
            # if STATION_PROBS are given as global priorities take first chunk of code
            # Start 1 #
            # plan_probs = np.random.uniform(0, 1, len(sim_env.stations))
            # current_station_plan = [sim_env.stations[i] for i in range(0, len(sim_env.stations)) if
            #                         plan_probs[i] <= sim_env.stationProbs[i]]
            # if sim_env.shuffleStations is True:
            #     current_station_plan = np.random.permutation(current_station_plan)
            #
            # sim_env.orderManager.generateOrder(np.random.choice(range(1, sim_env.orderManager.orderPriorities)),
            #                                    current_station_plan, sim_env.timeManager.simTime)
            # End 1 #

            # Start 2 #
            next_station = 0
            current_station_plan = [0]
            while next_station != len(sim_env.stationProbs) - 1:
                next_station = np.random.choice(range(0, len(sim_env.stationProbs[next_station])), p=sim_env.stationProbs[next_station])
                current_station_plan.append(next_station)
            current_station_plan = [sim_env.stations[i] for i in current_station_plan]
            sim_env.orderManager.generateOrder(np.random.choice(range(1, sim_env.orderManager.orderPriorities)),
                                               current_station_plan, sim_env.timeManager.simTime)
            # End 2 #

        # manage orders
        # check available stations
        available_stations = [s for s in sim_env.stations if s.available is True]

        # check available resources
        available_resources = [r for r in sim_env.resources if r.available is True]

        # check for idle orders
        idle_orders = [o for o in sim_env.orderManager.orderList if
                       o.idle is True and o.orderComplete is False]

        #Todo
        # - record place in queue for waiting before station

        # sort idle orders according to remaining time to deadline (according to station plan) and priority
        idle_orders.sort(key=lambda x: (x.timeToDeadline, x.orderPriority))

        # check for idle at machine orders
        idle_at_station_orders = [o for o in sim_env.orderManager.orderList if
                                  o.idleAtStation is True and o.orderComplete is False]

        # sort idle at station orders according to remaining time to deadline (according to station plan) and priority
        idle_at_station_orders.sort(key=lambda x: (x.timeToDeadline, x.orderPriority))

        # record station performance each iteration
        for station in sim_env.stations:
            station.performanceLog.append(station.performance)

        # assign idle at station orders, i.e. orders waiting at stations
        if len(idle_at_station_orders) > 0:
            for order in idle_at_station_orders:
                # assign free resource to the order waiting at a station
                if len(available_resources) != 0:
                    # let order wait at the desired station if no resource is available
                    # else assign resource to order
                    chosen_resource = np.random.choice(available_resources)
                    chosen_resource.available = False
                    order.setResource(chosen_resource)

                    # remove this resource from list of available resources
                    available_resources.pop(available_resources.index(chosen_resource))

                    # set idle at station status to false for this order
                    order.idleAtStation = False

        # assign orders
        if len(idle_orders) > 0:
            for order in idle_orders:
                next_station = order.getNextStation()
                # check if planned next station is available
                if len(available_stations) > 0 and next_station in available_stations:
                    # assign current order to the desired station
                    available_stations[available_stations.index(next_station)].available = False
                    order.setStation(available_stations[available_stations.index(next_station)])
                    order.idle = False

                    # remove this station from list of available stations
                    available_stations.pop(available_stations.index(next_station))

                if order.currentStation is not None and len(available_resources) == 0:
                    # let order wait at the desired station if no resource is available
                    order.idleAtStation = True
                elif order.currentStation is not None:
                    chosen_resource = np.random.choice(available_resources)
                    chosen_resource.available = False
                    order.setResource(chosen_resource)

                    # remove this resource from list of available resources
                    available_resources.pop(available_resources.index(chosen_resource))

                    # set idle at station status to false for this order
                    order.idleAtStation = False

        # work on the orders at stations with the assigned resources,
        # i.e. increment durations, set available or remain unavailable
        # stations and resources that are finishing orders in one iteration
        # are set to available but can start working only in the next iteration

        if len(sim_env.orderManager.orderList) > 0:
            for order in sim_env.orderManager.orderList:

                # deduct one time period from time to deadline for the order
                order.timeToDeadline -= 1

                if order.idle is True:
                    # record waiting times (in front of stations)
                    currentStationPlanIndices = [i for i, x in enumerate(order.stationPlan[:(len(order.stationLog)+1)]) if x == order.getNextStation()]
                    order.waitingTimeLog[currentStationPlanIndices[-1]] += 1
                elif order.idleAtStation is True:
                    # record waiting times at stations
                    currentStationPlanIndices = [i for i, x in enumerate(order.stationPlan[:len(order.stationLog)]) if x == order.currentStation]
                    order.waitingTimeAtStationLog[currentStationPlanIndices[-1]] += 1
                elif order.idle is False \
                        and order.idleAtStation is False \
                        and order.orderComplete is False:

                    # for testing if a station finishes their task the duration baseline is needed
                    # (and needs to be adjusted to introduce some variance)
                    # this is calculated once when the order is first processed at a station with a certain resource
                    if order.currentStationDuration is None:
                        baseline_duration = order.currentStation.durationBaseline
                        resource_productivity = order.currentResource.resourceProductivity
                        station_performance = order.currentStation.performance

                        individual_duration = round(
                            (baseline_duration / resource_productivity / station_performance) * np.random.normal(1,
                                                                                                                 0.05))
                        order.currentStationDuration = individual_duration

                    # record first working time at the station
                    if order.durationLog[len(order.stationLog)-1] == 0:
                        order.stationStartWorkingTimes.append(sim_env.timeManager.simTime)

                    # record cycle times
                    currentStationPlanIndices = [i for i, x in enumerate(order.stationPlan[:len(order.stationLog)]) if x == order.currentStation]
                    currentStationLogIndices = [i for i, x in enumerate(order.stationLog) if x == order.currentStation]
                    order.durationLog[currentStationPlanIndices[-1]] += 1
                    # order.durationLog[order.stationPlan.index(order.currentStation)] += 1
                    # adjust station performance due to station usage - check if station has below zero performance
                    order.currentStation.performance -= np.random.uniform(0, sim_env.maxDegradationPerPeriod)
                    if order.currentStation.performance < 0:
                        order.currentStation.performance = 0

                    # print(order.currentStationDuration)

                    # check if stations finish their task in this iteration
                    if order.durationLog[currentStationLogIndices[-1]] >= order.currentStationDuration:

                        # record mean performance at station
                        order.stationEndWorkingTimes.append(sim_env.timeManager.simTime)
                        workstart = order.stationStartWorkingTimes[-1]
                        workend = sim_env.timeManager.simTime

                        mean_performance = sum(
                            order.currentStation.performanceLog[workstart:workend]) / (workend - workstart)
                        order.meanPerformanceLog.append(mean_performance)

                        # send order to idle pool waiting for the next station of the order
                        # leave current station as attribute for purposes of waiting time recording
                        # if current station of the order is the last in the station plan send to completed orders
                        if len(order.stationPlan) == len(order.stationLog):
                            # orders with completeStatus == True remain in the order pool
                            # but are not assigned to stations or resources as they are neither idle nor idleAtMachine
                            # free resources and stations
                            order.currentStation.available = True
                            order.currentResource.available = True

                            order.orderComplete = True
                            order.unsetStation()

                            sim_env.orderManager.completedOrders.append(order)
                            sim_env.orderManager.orderList.pop(sim_env.orderManager.orderList.index(order))
                        else:
                            # free resources and stations
                            # set idle status for order
                            order.currentStation.available = True
                            order.currentResource.available = True

                            order.unsetStation()
                            order.idle = True

        # maintain stations when maintenance interval is reached (after all orders are worked on)
        if sim_env.timeManager.simTime % sim_env.maintenanceInterval == 0:
            for station in sim_env.stations:
                station.performance = 1

        # record the enterprise variables per iteration
        sim_env.stationsAvailable.append(len([station for station in sim_env.stations if station.available is True]))
        sim_env.resourcesAvailable.append(len([resource for resource in sim_env.resources if resource.available is True]))
        sim_env.existingOrders.append(len([order for order in sim_env.orderManager.orderList]))

        # record availabilities of stations and resources per iteration
        for station in sim_env.stations:
            station.availabilityLog.append(station.available)

        for resource in sim_env.resources:
            resource.availabilityLog.append(resource.available)

        #Todo
        # - record orders waiting in front of/before stations?
        # - record place in waiting line for each order in each iteration?
        # might be very complicated to export to an event log
        # place in line at start of waiting period for that activity/station? orders to be processed before me

        # increment simulation time
        sim_env.timeManager.simTime += 1

    print("...done!")
    return


def generate_event_log(simulated_enterprise):

    print("Generating event log...", end='')

    # form event log from all complete orders
    complete_orders = simulated_enterprise.orderManager.completedOrders

    order_dict = {}
    for order in complete_orders:
        order_dict[order.orderName] = {'count': len(order.stationLog),
                                       'init_time': order.initTime,
                                       'stations': order.stationLog,
                                       'mean_performances': order.meanPerformanceLog,
                                       'resources': order.resourceLog,
                                       'waiting_times': order.waitingTimeLog,
                                       'waiting_times_at_stations': order.waitingTimeAtStationLog,
                                       'durations': order.durationLog}

    # fill the columns for the data frame
    order_col = np.concatenate([np.repeat(entry, order_dict.get(entry).get('count')) for entry in order_dict])
    station_col = [station.stationName for station in
                   np.concatenate([order_dict.get(entry).get('stations') for entry in order_dict])]
    mean_performance_col = np.concatenate([order_dict.get(entry).get('mean_performances') for entry in order_dict])
    resource_col = [resource.resourceName for resource in
                    np.concatenate([order_dict.get(entry).get('resources') for entry in order_dict])]
    productivity_col = [resource.resourceProductivity for resource in
                        np.concatenate([order_dict.get(entry).get('resources') for entry in order_dict])]
    waiting_time_col = np.concatenate([order_dict.get(entry).get('waiting_times') for entry in order_dict])
    waiting_time_at_stations_col = np.concatenate([order_dict.get(entry).get('waiting_times_at_stations')
                                                   for entry in order_dict])
    duration_col = np.concatenate([order_dict.get(entry).get('durations') for entry in order_dict])

    timestamp_in_col = np.concatenate([np.repeat(order_dict.get(entry).get('init_time'),
                                                 order_dict.get(entry).get('count')) for entry in order_dict])

    # initialize further timestamp columns for saving times of the different
    # process instances (i.e. waiting, working, etc.)
    timestamp_at_station_col = [0] * len(order_col)
    timestamp_start_work_col = [0] * len(order_col)
    timestamp_out_col = [0] * len(order_col)

    last_time = -1
    current_order = -1

    # calculate different timestamps for all orders and the traversed stations
    for i in range(0, len(order_col)):

        if current_order != order_col[i]:
            last_time = -1
            current_order = order_col[i]

        if last_time >= 0:
            timestamp_in_col[i] = last_time

        timestamp_at_station_col[i] += timestamp_in_col[i] + \
                                       waiting_time_col[i]

        timestamp_start_work_col[i] += timestamp_in_col[i] + \
                                       waiting_time_col[i] + \
                                       waiting_time_at_stations_col[i]

        timestamp_out_col[i] += timestamp_in_col[i] + \
                                waiting_time_col[i] + \
                                waiting_time_at_stations_col[i] + \
                                duration_col[i]

        last_time = timestamp_out_col[i]

    # recode timestamp columns to actual timestamps
    start_time = datetime.timestamp(datetime(2020, 1, 1, 0, 0, 0, 0))
    timestamp_in_col = [datetime.fromtimestamp(start_time + timestamp) for timestamp in timestamp_in_col]
    timestamp_at_station_col = [datetime.fromtimestamp(start_time + timestamp) for
                                timestamp in timestamp_at_station_col]
    timestamp_start_work_col = [datetime.fromtimestamp(start_time + timestamp) for
                                timestamp in timestamp_start_work_col]
    timestamp_out_col = [datetime.fromtimestamp(start_time + timestamp) for timestamp in timestamp_out_col]

    # make DataFrame from all columns
    event_log_frame = pd.DataFrame([order_col,
                                    station_col,
                                    mean_performance_col,
                                    resource_col,
                                    productivity_col,
                                    waiting_time_col,
                                    waiting_time_at_stations_col,
                                    duration_col,
                                    timestamp_in_col,
                                    timestamp_at_station_col,
                                    timestamp_start_work_col,
                                    timestamp_out_col]).transpose()

    # assign meaningful column names
    event_log_frame.columns = ["order_id",
                               "station",
                               "mean_performance",
                               "resource",
                               "resource_productivity",
                               "waiting_time",
                               "waiting_time_at_station",
                               "duration",
                               "timestamp_in",
                               "timestamp_at_station",
                               "timestamp_start_work",
                               "timestamp_out"]
    print("done!")
    return event_log_frame

def generate_enterprise_log(simulated_enterprise, relevant_indices):
    print("Generating enterprise log...", end='')

    # form enterprise log
    # fill the columns for the data frame
    start_time = datetime.timestamp(datetime(2020, 1, 1, 0, 0, 0, 0))
    timestamp_col = [datetime.fromtimestamp(start_time + iteration) for iteration in range(0, simulated_enterprise.timeManager.simDuration)]
    timestamp_col = [timestamp_col[index] for index in relevant_indices]
    stations_available_col = [simulated_enterprise.stationsAvailable[index] for index in relevant_indices]
    resources_available_col = [simulated_enterprise.resourcesAvailable[index] for index in relevant_indices]
    existing_orders_col = [simulated_enterprise.existingOrders[index] for index in relevant_indices]

    station_dict = {}
    for station in simulated_enterprise.stations:
        station_dict[station.stationName] = [station.availabilityLog[index] for index in relevant_indices]

    resource_dict = {}
    for resource in simulated_enterprise.resources:
        resource_dict[resource.resourceName] = [resource.availabilityLog[index] for index in relevant_indices]

    # make DataFrame from all columns
    enterprise_log_frame = pd.DataFrame([timestamp_col,
                                         stations_available_col,
                                         resources_available_col,
                                         existing_orders_col]).transpose()

    # assign meaningful column names
    enterprise_log_frame.columns = ["timestamp",
                                    "stations_available",
                                    "resources_available",
                                    "existing_orders"]

    for entry in station_dict:
        enterprise_log_frame["station_" + str(entry) + "_available"] = station_dict[entry]

    for entry in resource_dict:
        enterprise_log_frame["resource_" + str(entry) + "_available"] = resource_dict[entry]

    print("done!")
    return enterprise_log_frame

def generate_parameter_frame(simulated_enterprise):
    print("Generating simulation parameters...", end='')

    # form enterprise log
    # fill the columns for the data frame
    station_names = [station.stationName for station in simulated_enterprise.stations]
    station_duration_baselines = [station.durationBaseline for station in simulated_enterprise.stations]
    station_execution_probabilities = [station.executionProb for station in simulated_enterprise.stations]

    resource_names = [resource.resourceName for resource in simulated_enterprise.resources]
    resource_productivities = [resource.resourceProductivity for resource in simulated_enterprise.resources]

    # make DataFrame from columns
    station_frame = pd.DataFrame([station_names,
                                  station_duration_baselines,
                                  station_execution_probabilities]).transpose()

    # make DataFrame from columns
    resource_frame = pd.DataFrame([resource_names,
                                   resource_productivities]).transpose()

    # assign meaningful column names
    station_frame.columns = ["station_name",
                             "station_duration_baseline",
                             "station_execution_probability"]

    resource_frame.columns = ["resource_name",
                              "resource_productivity"]

    print("done!")
    return station_frame, resource_frame

def export_event_log(log, filename):
    print("Exporting event log...", end='')
    log.to_csv(filename, index=False, sep=',')
    print("done!")
    return

def export_enterprise_log(log, filename):
    print("Exporting enterprise log...", end='')
    log.to_csv(filename, index=False, sep=',')
    print("done!")
    return

def export_parameter_frames(station_log, resource_log, station_filename, resource_filename):
    print("Exporting enterprise parameters...", end='')
    station_log.to_csv(station_filename, index=False, sep=',')
    resource_log.to_csv(resource_filename, index=False, sep=',')
    print("done!")
    return

if __name__ == '__main__':

    #########################
    # SIMULATION PARAMETERS #
    #########################

    config_files = os.listdir("configs/")

    for config_file in config_files:

        # config_file="500_stations_UNIFORM_UPPER_TRIANGLE.json"
        with open("configs/" + config_file) as f:
            params = json.load(f)

        params["MAX_DEGRADATION_PER_PERIOD"] = 1/params["MAINTENANCE_INTERVAL"]

        # # number of different activities
        # STATION_COUNT = 10
        # # execution probabilities of activities
        # # STATION_PROBS = [1, 1, 0.8, 0.5, 1, 0.75, 0.8, 0.5, 1, 1]
        # STATION_PROBS = [[0.0, 0.8, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        #                  [0.0, 0.0, 0.9, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        #                  [0.0, 0.0, 0.0, 0.4, 0.3, 0.3, 0.0, 0.0, 0.0, 0.0],
        #                  [0.0, 0.0, 0.0, 0.0, 0.3, 0.2, 0.4, 0.1, 0.0, 0.0],
        #                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.8, 0.2, 0.0, 0.0, 0.0],
        #                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.1, 0.0, 0.0],
        #                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.0],
        #                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6, 0.4],
        #                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        #                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
        # # duration baselines for each individual station in seconds
        # STATION_DURATIONS = [100, 200, 20, 60, 300, 500, 300, 100, 250, 60]
        # # shuffle the stations for each order after stations are planned?
        # SHUFFLE_STATIONS = False
        # # how often are stations maintained?
        # MAINTENANCE_INTERVAL = 60*60
        # # how fast are stations degrading due to usage - max performance is 1, i.e. 100%
        # MAX_DEGRADATION_PER_PERIOD = 1/MAINTENANCE_INTERVAL
        # # number of available resources to work at stations
        # RESOURCE_COUNT = 4
        # # productivities of different resources
        # RESOURCE_PRODUCTIVITIES = [0.75, 0.8, 0.8, 0.9, 1, 1, 1.2, 1.2, 1.5, 1.5]
        # # total simulation duration in seconds
        # SIM_DURATION = round(1 * 60 * 60 * 24)
        # # frequency of order generation per second, i.e. probability per second for generation of order
        # ORDER_FREQUENCY = 1/(60*10)  # one order every ten minutes
        # # number of order priorities
        # ORDER_PRIORITIES = 5

        #########################
        #########################
        #########################

        # # initializing the enterprise for the simulation
        # sim_enterprise = enterprise.Enterprise(enterprise_name="Enterprise",
        #                                        n_stations=params["STATION_COUNT"],
        #                                        station_names=range(0, params["STATION_COUNT"]),
        #                                        station_probs=params["STATION_PROBS"],
        #                                        station_durations=params["STATION_DURATIONS"],
        #                                        shuffle_stations=params["SHUFFLE_STATIONS"],
        #                                        maintenance_interval=params["MAINTENANCE_INTERVAL"],
        #                                        max_degradation_per_period=params["MAX_DEGRADATION_PER_PERIOD"],
        #                                        n_resources=params["RESOURCE_COUNT"],
        #                                        resource_names=range(0, params["RESOURCE_COUNT"]),
        #                                        resource_productivities=params["RESOURCE_PRODUCTIVITIES"],
        #                                        sim_duration=params["SIM_DURATION"],
        #                                        order_freq=params["ORDER_FREQUENCY"],
        #                                        order_priorities=params["ORDER_PRIORITIES"])
        
        # ensuring log completion (focus on control flow)
        sim_enterprise = enterprise.Enterprise(enterprise_name="Enterprise",
                                            n_stations=params["STATION_COUNT"],
                                            station_names=range(0, params["STATION_COUNT"]),
                                            station_probs=params["STATION_PROBS"],
                                            station_durations=[150 for i in range(0, params["STATION_COUNT"])],
                                            shuffle_stations=params["SHUFFLE_STATIONS"],
                                            maintenance_interval=params["MAINTENANCE_INTERVAL"],
                                            max_degradation_per_period=params["MAX_DEGRADATION_PER_PERIOD"],
                                            n_resources=params["STATION_COUNT"],
                                            resource_names=range(0, params["STATION_COUNT"]),
                                            resource_productivities=[1 for i in range(0, params["STATION_COUNT"])],
                                            sim_duration=params["SIM_DURATION"],
                                            order_freq=params["ORDER_FREQUENCY"],
                                            order_priorities=params["ORDER_PRIORITIES"])


        # run the simulation in the generated enterprise
        simulate(sim_enterprise)

        # generate an event log from the simulated enterprise data
        event_log = generate_event_log(sim_enterprise)

        if not os.path.exists("export/" + os.path.splitext(config_file)[0]):
            os.mkdir("export/" + os.path.splitext(config_file)[0])

        # export the generated event log for the simulation
        export_event_log(event_log, "export/" + os.path.splitext(config_file)[0] + "/sim_event_log_" + os.path.splitext(config_file)[0] + ".csv")

        all_event_timestamps = event_log["timestamp_in"].to_list() + event_log["timestamp_at_station"].to_list() + event_log["timestamp_start_work"].to_list() + event_log["timestamp_out"].to_list()
        relevant_indices = [i for i, x in enumerate(pd.Series([datetime.fromtimestamp(datetime.timestamp(datetime(2020, 1, 1, 0, 0, 0, 0)) + iteration) for iteration in range(0, sim_enterprise.timeManager.simDuration)]).isin(set(all_event_timestamps)).to_list()) if x]

        # generate the enterprise log with occupations per iteration
        enterprise_log = generate_enterprise_log(sim_enterprise, relevant_indices)

        # export the generated enterprise log for the simulation
        export_enterprise_log(enterprise_log, "export/" + os.path.splitext(config_file)[0] + "/sim_enterprise_log_" + os.path.splitext(config_file)[0] + ".csv")

        # generate DataFrame of station and resource parameters
        station_frame, resource_frame = generate_parameter_frame(sim_enterprise)

        # export generated parameter DataFrame
        export_parameter_frames(station_frame, resource_frame, "export/" + os.path.splitext(config_file)[0] + "/stations_" + os.path.splitext(config_file)[0] + ".csv", "export/" + os.path.splitext(config_file)[0] + "/resources_" + os.path.splitext(config_file)[0] + ".csv")

        print("Simulation and data export completed! Have fun with your simulated process data (■_■¬)")
