# This class represents a process station/activity

class Station:

    def __init__(self, station_name, execution_prob, duration_baseline):

        self.stationName = station_name
        self.executionProb = execution_prob
        self.durationBaseline = duration_baseline

        self.performance = 1
        self.available = True


    def setAvailability(self, availability):
        self.available = availability
        return

    def getAvailability(self):
        return self.available

    def getDurationBaseline(self):
        return self.durationBaseline

    def getStationName(self):
        return self.stationName

    def getPerformance(self):
        return self.performance

    def setPerformance(self, value):
        self.performance = value
        return

    def decreasePerformance(self, adjustment):
        self.performance -= adjustment
        return
