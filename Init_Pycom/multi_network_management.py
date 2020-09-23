""" Class to store a list of networks, msgflows and allocations """

from msgflow import MessageFlow
from network_algo import Network
from allocation import Allocation

class multi_network_management():
    """ Class to store a list of networks, msgflows and allocations """
    list_networks = []
    list_msgflows = []
    list_allocations = []

    def allocate(self, msgflow, network, critlevel):
        """ Allocate a msgflow of a certain criticality to a network """
        # Deallocate if existing
        self.deallocate(msgflow)
        # Append to the list of allocation
        self.list_allocations.append(Allocation(msgflow, network, critlevel))


    def deallocate(self, msgflow):
        """ De-allocate a msgflow if it is allocated """
        # Find the old allocation
        old_alloc = self.get_allocation_by_msgflow(msgflow)

        # If found, delete it from the list
        if old_alloc is not None:
            print("Old allocation found")
            self.list_allocations.remove(old_alloc)


    def get_allocation_by_msgflow(self, msgflow):
        """ Find the msgflow allocation in the list list_allocation """
        for i in self.list_allocations:
            if i.get_flow() == msgflow:
                return i
        return None

    def print_all_allocation(self):
        """ Print all the allocated msgflows """
        for i in self.list_allocations:
            i.to_string()

def main():
    """ Testing """

    flow1 = MessageFlow("1.Hello", 2, 20, 0.02)
    flow2 = MessageFlow("2.Hello", 2, 20, 0.02)
    network1 = Network("Wi-Fi", True, 80, -1, -1)
    mnm = multi_network_management()

    all1 = mnm.allocate(flow1, network1, 0)
    all2 = mnm.allocate(flow2, network1, 0)
    mnm.print_all_allocation()


if __name__ == '__main__':
    main()
