# This class represents an order (case) that traverses the enterprise through different stations


class Order:

    def __init__(self, order_name, order_priority, station_plan, init_time):

        self.orderName = order_name
        self.orderPriority = order_priority
        self.stationPlan = station_plan  # planned stations that have to be executed before the order is finished
        self.stationLog = []  # list of stations that were visited during the lifetime of the order
        self.resourceLog = []  # list of resources that worked on the order during the lifetime of the order
        self.durationLog = []  # list of durations at stations that were visited during the lifetime of the order
        self.waitingTimeLog = [0]  # list of waiting times in front of stations during the lifetime of the order
        self.waitingTimeAtStationLog = []  # list of waiting times at stations during the lifetime of the order
        self.idle = True
        self.idleAtStation = False
        self.orderComplete = False
        self.initTime = init_time

        self.currentStation = None
        self.currentResource = None
        self.currentStationDuration = None

    def getOrderName(self):
        return self.orderName

    def getStationPlan(self):
        return self.stationPlan

    def getNextStation(self):
        # check stationLog
        # which station is the next one?
        if len(self.stationLog) == 0:
            return self.stationPlan[0]
        else:
            return self.stationPlan[self.stationPlan.index(self.stationLog[-1]) + 1]

    def getCurrentStation(self):
        return self.currentStation

    def getCurrentResource(self):
        return self.currentResource

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

    def setIdleStatus(self, idle_status):
        self.idle = idle_status
        return

    def setIdleAtStationStatus(self, idle_at_station_status):
        self.idleAtStation = idle_at_station_status
        return

    def getIdleStatus(self):
        return self.idle

    def getIdleAtStationStatus(self):
        return self.idleAtStation

    def getOrderPriority(self):
        return self.orderPriority

    def checkDuration(self, station):
        return self.durationLog[self.stationLog.index(station)]

    def incrementDuration(self, station, amount):
        self.durationLog[self.stationLog.index(station)] += amount
        return

    def incrementWaitingTime(self, station, amount):
        self.waitingTimeLog[self.stationPlan.index(station)] += amount
        return

    def incrementWaitingTimeAtStation(self, station, amount):
        self.waitingTimeAtStationLog[self.stationLog.index(station)] += amount
        return

    def getCompleteStatus(self):
        return self.orderComplete

    def setCompleteStatus(self, complete_status):
        self.orderComplete = complete_status
        return

    def getStationLog(self):
        return self.stationLog

    def getResourceLog(self):
        return self.resourceLog

    def getDurationLog(self):
        return self.durationLog

    def getWaitingTimeLog(self):
        return self.waitingTimeLog

    def getWaitingTimeAtStationLog(self):
        return self.waitingTimeAtStationLog

    def getInitTime(self):
        return self.initTime

    def setCurrentStationDuration(self, value):
        self.currentStationDuration = value
        return

    def getCurrentStationDuration(self):
        return self.currentStationDuration

    # def setWaitingTime(self, amount):
    #     self.waitingTime = amount
    #
    # def getWaitingTime(self):
    #     return self.waitingTime
    #
    # def setWaitingTimeAtStations(self, amount):
    #     self.waitingTimeAtStations = amount
    #
    # def getWaitingTimeAtStations(self):
    #     return self.waitingTimeAtStations