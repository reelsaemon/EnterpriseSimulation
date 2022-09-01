# This is a simulation environment for generating enterprise data
# suitable for duration prediction purposes
# The data output after the simulation should form an event log
# with different activities/process steps that depend on some
# process variables that are modelled individually for each activity

import enterprise
import numpy as np
import pandas as pd
from datetime import datetime
from tqdm import tqdm


def simulate(sim_env):
    print("Simulating...")

    # simulation step
    for sim_step in tqdm(range(sim_env.timeManager.simDuration)):

        # simulate one iteration

        # # one order
        # if(sim_env.timeManager.getTime() == 0):
        #     plan_probs = np.random.uniform(0, 1, len(sim_env.stations))
        #     current_station_plan = [sim_env.stations[i] for i in range(0, len(sim_env.stations)) if
        #                             plan_probs[i] <= sim_env.stationProbs[i]]
        #     sim_env.orderManager.generateOrder(np.random.choice(range(1, sim_env.orderManager.getOrderPriorities())),
        #                                        current_station_plan, sim_env.timeManager.getTime())

        # generate new orders
        # roll if order is to be generated this iteration
        # roll for order priority
        # include functionality for shuffling the planned stations (optional)
        if np.random.uniform() <= sim_env.orderManager.getOrderFrequency():
            plan_probs = np.random.uniform(0, 1, len(sim_env.stations))
            current_station_plan = [sim_env.stations[i] for i in range(0, len(sim_env.stations)) if
                                    plan_probs[i] <= sim_env.stationProbs[i]]
            if sim_env.shuffleStations is True:
                current_station_plan = np.random.permutation(current_station_plan)

            sim_env.orderManager.generateOrder(np.random.choice(range(1, sim_env.orderManager.getOrderPriorities())),
                                               current_station_plan, sim_env.timeManager.getTime())

        # manage orders
        # check available stations
        available_stations = [s for s in sim_env.stations if s.getAvailability() is True]

        # check available resources
        available_resources = [r for r in sim_env.resources if r.getAvailability() is True]

        # check for idle orders
        idle_orders = [o for o in sim_env.orderManager.getOrderList() if
                       o.getIdleStatus() is True and o.getCompleteStatus() is False]

        # sort idle orders according to priority
        idle_orders.sort(key=lambda x: x.getOrderPriority())

        # check for idle at machine orders
        idle_at_station_orders = [o for o in sim_env.orderManager.getOrderList() if
                                  o.getIdleAtStationStatus() is True and o.getCompleteStatus() is False]

        idle_at_station_orders.sort(key=lambda x: x.getOrderPriority())

        # assign idle at station orders, i.e. orders waiting at stations
        if len(idle_at_station_orders) > 0:
            for order in idle_at_station_orders:
                # assign free resource to the order waiting at a station
                if len(available_resources) != 0:
                    # let order wait at the desired station if no resource is available
                    # else assign resource to order
                    chosen_resource = np.random.choice(available_resources)
                    chosen_resource.setAvailability(False)
                    order.setResource(chosen_resource)

                    # remove this resource from list of available resources
                    available_resources.pop(available_resources.index(chosen_resource))

                    # set idle at station status to false for this order
                    order.setIdleAtStationStatus(False)

        # assign orders
        if len(idle_orders) > 0:
            for order in idle_orders:
                next_station = order.getNextStation()
                # check if planned next station is available
                if len(available_stations) > 0 and next_station in available_stations:
                    # assign current order to the desired station
                    available_stations[available_stations.index(next_station)].setAvailability(False)
                    order.setStation(available_stations[available_stations.index(next_station)])
                    order.setIdleStatus(False)

                    # remove this station from list of available stations
                    available_stations.pop(available_stations.index(next_station))

                if order.getCurrentStation() is not None and len(available_resources) == 0:
                    # let order wait at the desired station if no resource is available
                    order.setIdleAtStationStatus(True)
                elif order.getCurrentStation() is not None:
                    chosen_resource = np.random.choice(available_resources)
                    chosen_resource.setAvailability(False)
                    order.setResource(chosen_resource)

                    # remove this resource from list of available resources
                    available_resources.pop(available_resources.index(chosen_resource))

                    # set idle at station status to false for this order
                    order.setIdleAtStationStatus(False)

        # work on the orders at stations with the assigned resources,
        # i.e. increment durations, set available or remain unavailable
        # stations and resources that are finishing orders in one iteration
        # are set to available but can start working only in the next iteration

        if len(sim_env.orderManager.getOrderList()) > 0:
            for order in sim_env.orderManager.getOrderList():

                if order.getIdleStatus() is True:
                    # record waiting times (in front of stations)
                    order.incrementWaitingTime(order.getNextStation(), 1)
                elif order.getIdleAtStationStatus() is True:
                    # record waiting times at stations
                    order.incrementWaitingTimeAtStation(order.getCurrentStation(), 1)
                elif order.getIdleStatus() is False \
                        and order.getIdleAtStationStatus() is False \
                        and order.getCompleteStatus() is False:

                    # for testing if a station finishes their task the duration baseline is needed
                    # (and needs to be adjusted to introduce some variance)
                    # this is calculated once when the order is first processed at a station with a certain resource
                    if order.getCurrentStationDuration() is None:
                        baseline_duration = order.getCurrentStation().getDurationBaseline()
                        resource_productivity = order.getCurrentResource().getResourceProductivity()
                        station_performance = order.getCurrentStation().getPerformance()

                        individual_duration = round(
                            (baseline_duration / resource_productivity / station_performance) * np.random.normal(1,
                                                                                                                 0.05))
                        order.setCurrentStationDuration(individual_duration)

                    # record cycle times
                    order.incrementDuration(order.getCurrentStation(), 1)
                    # adjust station performance due to station usage - check if station has below zero performance
                    order.getCurrentStation().decreasePerformance(np.random.uniform(0, sim_env.maxDegradationPerPeriod))
                    if order.getCurrentStation().getPerformance() < 0:
                        order.getCurrentStation().setPerformance(0)

                    # check if stations finish their task in this iteration
                    if order.checkDuration(order.currentStation) >= order.getCurrentStationDuration():
                        # send order to idle pool waiting for the next station of the order
                        # leave current station as attribute for purposes of waiting time recording
                        # if current station of the order is the last in the station plan send to completed orders
                        if len(order.getStationPlan()) == len(order.getStationLog()):
                            # orders with completeStatus == True remain in the order pool
                            # but are not assigned to stations or resources as they are neither idle nor idleAtMachine
                            # free resources and stations
                            order.getCurrentStation().setAvailability(True)
                            order.getCurrentResource().setAvailability(True)

                            order.setCompleteStatus(True)
                            order.unsetStation()

                            sim_env.orderManager.getCompletedOrdersList().append(order)
                            sim_env.orderManager.getOrderList().pop(sim_env.orderManager.getOrderList().index(order))
                        else:
                            # free resources and stations
                            # set idle status for order
                            order.getCurrentStation().setAvailability(True)
                            order.getCurrentResource().setAvailability(True)

                            order.unsetStation()
                            order.setIdleStatus(True)

        # maintain stations when maintenance interval is reached (after all orders are worked on)
        if sim_env.timeManager.getTime() % sim_env.maintenanceInterval == 0:
            for station in sim_env.stations:
                station.setPerformance(1)

        # increment simulation time
        sim_env.timeManager.setTime(sim_env.timeManager.getTime() + 1)

    print("...done!")
    return


def generate_event_log(simulated_enterprise):

    print("Generating event log...", end='')

    # form event log from all complete orders
    complete_orders = simulated_enterprise.orderManager.getCompletedOrdersList()

    order_dict = {}
    for order in complete_orders:
        order_dict[order.getOrderName()] = {'count': len(order.getStationLog()),
                                            'init_time': order.getInitTime(),
                                            'stations': order.getStationLog(),
                                            'resources': order.getResourceLog(),
                                            'waiting_times': order.getWaitingTimeLog(),
                                            'waiting_times_at_stations': order.getWaitingTimeAtStationLog(),
                                            'durations': order.getDurationLog()}

    # fill the columns for the data frame
    order_col = np.concatenate([np.repeat(entry, order_dict.get(entry).get('count')) for entry in order_dict])
    station_col = [station.getStationName() for station in
                   np.concatenate([order_dict.get(entry).get('stations') for entry in order_dict])]
    resource_col = [resource.getResourceName() for resource in
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
    log_frame = pd.DataFrame([order_col,
                              station_col,
                              resource_col,
                              waiting_time_col,
                              waiting_time_at_stations_col,
                              duration_col,
                              timestamp_in_col,
                              timestamp_at_station_col,
                              timestamp_start_work_col,
                              timestamp_out_col]).transpose()

    # assign meaningful column names
    log_frame.columns = ["order_id",
                         "station",
                         "resource",
                         "waiting_time",
                         "waiting_time_at_station",
                         "duration",
                         "timestamp_in",
                         "timestamp_at_station",
                         "timestamp_start_work",
                         "timestamp_out"]
    print("done!")
    return log_frame


def export_event_log(log, filename):
    print("Exporting event log...", end='')
    log.to_csv(filename, index=False, sep=';')
    print("done!\n")
    return


if __name__ == '__main__':

    #########################
    # SIMULATION PARAMETERS #
    #########################

    # number of different activities
    STATION_COUNT = 10
    # execution probabilities of activities
    STATION_PROBS = [1, 1, 0.8, 0.5, 1, 0.75, 0.8, 0.5, 1, 1]
    # duration baselines for each individual station in seconds
    STATION_DURATIONS = [600, 1020, 120, 60, 600, 3000, 300, 600, 1200, 60]
    # shuffle the stations for each order after stations are planned?
    SHUFFLE_STATIONS = False
    # how often are stations maintained?
    MAINTENANCE_INTERVAL = 60*60
    # how fast are stations degrading due to usage - max performance is 1, i.e. 100%
    MAX_DEGRADATION_PER_PERIOD = 1/MAINTENANCE_INTERVAL
    # number of available resources to work at stations
    RESOURCE_COUNT = 8
    # productivities of different resources
    RESOURCE_PRODUCTIVITIES = [0.75, 0.8, 0.8, 0.9, 1, 1, 1.2, 1.2, 1.5, 1.5]
    # total simulation duration in seconds
    SIM_DURATION = 1 * 60 * 60 * 24
    # frequency of order generation per second, i.e. probability per second for generation of order
    ORDER_FREQUENCY = 1/60  # one order per minute
    # number of order priorities
    ORDER_PRIORITIES = 5
    # loops in execution allowed? ---not implemented yet---
    ALLOW_LOOPS = False

    #########################
    #########################
    #########################

    # initializing the enterprise for the simulation
    sim_enterprise = enterprise.Enterprise(enterprise_name="Enterprise",
                                           n_stations=STATION_COUNT,
                                           station_names=range(0, STATION_COUNT),
                                           station_probs=STATION_PROBS,
                                           station_durations=STATION_DURATIONS,
                                           shuffle_stations=SHUFFLE_STATIONS,
                                           maintenance_interval=MAINTENANCE_INTERVAL,
                                           max_degradation_per_period=MAX_DEGRADATION_PER_PERIOD,
                                           n_resources=RESOURCE_COUNT,
                                           resource_names=range(0, RESOURCE_COUNT),
                                           resource_productivities=RESOURCE_PRODUCTIVITIES,
                                           sim_duration=SIM_DURATION,
                                           order_freq=ORDER_FREQUENCY,
                                           order_priorities=ORDER_PRIORITIES)

    # run the simulation in the generated enterprise
    simulate(sim_enterprise)

    # generate an event log from the simulated enterprise data
    event_log = generate_event_log(sim_enterprise)

    # export the generated event log for the simulation
    export_event_log(event_log, "export/sim_enterprise.csv")

    print("Simulation and data export completed! Have fun with your simulated process data (■_■¬)")
