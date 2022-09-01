# This class works as the simulation time manager
# It specifies how long the simulation has to run and can be used to check the simulation time

class TimeManager:

    def __init__(self, manager_name, sim_duration):

        self.ManagerName = manager_name
        self.simDuration = sim_duration

        self.simTime = 0  # counter variable for simulation time

    def getTime(self):
        return self.simTime

    def setTime(self, amount):
        self.simTime = amount

    def getSimDuration(self):
        return self.simDuration
