# This class represents a process station/activity

class Station:

    def __init__(self, station_name, execution_prob, duration_baseline):

        self.stationName = station_name
        self.executionProb = execution_prob
        self.durationBaseline = duration_baseline

        self.performance = 1
        self.available = True
        self.performanceLog = []
