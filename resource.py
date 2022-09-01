# This class represents a resource (worker) that executes tasks at a station

class Resource:

    def __init__(self, resource_name, resource_productivity):
        self.resourceName = resource_name
        self.resourceProductivity = resource_productivity
        self.available = True

    def setAvailability(self, availability):
        self.available = availability
        return

    def getAvailability(self):
        return self.available

    def getResourceName(self):
        return self.resourceName

    def getResourceProductivity(self):
        return self.resourceProductivity
