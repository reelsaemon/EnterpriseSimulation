# The Enterprise class combines all parts of the enterprise, i.e. stations, resources, managers, in one instance

import station
import resource
import ordermanager
import timemanager


class Enterprise:

    def __init__(self,
                 enterprise_name,
                 n_stations,
                 station_names,
                 station_probs,
                 station_durations,
                 shuffle_stations,
                 maintenance_interval,
                 max_degradation_per_period,
                 n_resources,
                 resource_names,
                 resource_productivities,
                 sim_duration,
                 order_freq,
                 order_priorities):

        print("Initializing enterprise...", end='')

        self.enterpriseName = enterprise_name
        self.stations = [station.Station(station_names[i],
                                         station_probs[i],
                                         station_durations[i]) for i in range(0, n_stations)]
        self.stationProbs = station_probs
        self.shuffleStations = shuffle_stations
        self.maintenanceInterval = maintenance_interval
        self.maxDegradationPerPeriod = max_degradation_per_period
        self.resources = [resource.Resource(resource_names[i],
                                            resource_productivities[i]) for i in range(0, n_resources)]
        self.timeManager = timemanager.TimeManager("TimeManager", sim_duration)
        self.orderManager = ordermanager.OrderManager("OrderManager", order_freq, order_priorities)

        self.stationsAvailable = []
        self.resourcesAvailable = []
        self.existingOrders = []

        print("done!")
