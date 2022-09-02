# This class represents a resource (worker) that executes tasks at a station

class Resource:

    def __init__(self, resource_name, resource_productivity):
        self.resourceName = resource_name
        self.resourceProductivity = resource_productivity
        self.available = True
