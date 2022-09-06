# This class represents an order (case) that traverses the enterprise through different stations


class Order:

    def __init__(self, order_name, order_priority, station_plan, init_time):

        self.orderName = order_name
        self.orderPriority = order_priority
        self.stationPlan = station_plan  # planned stations that have to be executed before the order is finished
        self.initTime = init_time

        self.stationLog = []  # list of stations that were visited during the lifetime of the order
        self.meanPerformanceLog = []  # list of mean performance for each station visited throughout the process
        self.resourceLog = []  # list of resources that worked on the order during the lifetime of the order
        self.durationLog = []  # list of durations at stations that were visited during the lifetime of the order
        self.waitingTimeLog = [0]  # list of waiting times in front of stations during the lifetime of the order
        self.waitingTimeAtStationLog = []  # list of waiting times at stations during the lifetime of the order
        self.queueLog = [] # list of place in queue when waiting for a certain station
        self.idle = True
        self.idleAtStation = False
        self.orderComplete = False
        self.stationStartWorkingTimes = []  # list of times when stations are entered and the order is being worked
        self.stationEndWorkingTimes = []  # list of times when stations are left after the order was being worked
        self.currentStation = None
        self.currentResource = None
        self.currentStationDuration = None
        self.timeToDeadline = sum([station.durationBaseline for station in self.stationPlan])

    def getNextStation(self):
        # check stationLog
        # which station is the next one?
        if len(self.stationLog) == 0:
            return self.stationPlan[0]
        else:
            return self.stationPlan[self.stationPlan.index(self.stationLog[-1]) + 1]

    def setResource(self, resource):
        self.resourceLog.append(resource)
        self.currentResource = resource
        return

    def setStation(self, station):
        self.stationLog.append(station)
        self.currentStation = station
        self.durationLog.append(0)
        self.waitingTimeAtStationLog.append(0)
        return

    def unsetStation(self):
        self.currentStation = None
        self.currentResource = None
        self.currentStationDuration = None

        if self.orderComplete is False:
            self.waitingTimeLog.append(0)
        return
