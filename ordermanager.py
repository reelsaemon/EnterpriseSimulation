# This class represents a manager that initializes the incoming orders

import order


class OrderManager:

    def __init__(self, manager_name, order_frequency, order_priorities):

        self.ManagerName = manager_name
        self.orderFrequency = order_frequency
        self.orderPriorities = order_priorities

        self.orderCount = 0
        self.orderList = list()
        self.completedOrders = list()

    def generateOrder(self, order_priority, station_plan, init_time):
        self.orderCount += 1
        new_order = order.Order(self.orderCount, order_priority, station_plan, init_time)
        self.orderList.append(new_order)
        return
