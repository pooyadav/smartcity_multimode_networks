""" Class to store a list of networks, msgflows and allocations """
from msgflow import MessageFlow
from network_algo import Network
from allocation import Allocation
#from multi_network_management import multi_network_management
from binpacking.message_flow_element import MessageFlowElement
from binpacking.network_bin import NetworkBin

class multi_network_management():
    """ Class to store a list of networks, msgflows and allocations """
    # Multi Network Management
    num_crit_levels = 6
    list_networks = []
    list_msgflows = []
    list_allocations = []
    # Utilisation based MultiNetwork Mangement
    list_elements = []
    list_unallocated_elements = []
    list_bins = []
    list_criticalities = [None] * num_crit_levels
    decreasing = False
    highest = True
    best = False
    worst = False
    first = False

    for i in range(0, num_crit_levels):
        list_criticalities[i] = []


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

    def add_msgflow(self, msgflow):
        """ Add msgflow in the list_msgflow and elements based on criticality"""
        self.list_msgflows.append(msgflow)

        if self.highest:
            mfe = MessageFlowElement(msgflow, msgflow.get_highest_criticality())
            self.list_elements.append(mfe)
        else:
            mfe = MessageFlowElement(msgflow, msgflow.get_lowest_criticality())
            self.list_elements.append(mfe)

    def add_network(self, network):
        """ Add the network to list_networks and list_bins """
        self.list_networks.append(network)
        # Create a instance of Network Bin and append to the list_bins
        self.list_bins.append(NetworkBin(network))

    def get_largest_bin(self):
        """ Find the network bin with the largest capacity (currently bandwidth) """
        largest = None
        iter_list_bins = iter(self.list_bins)
        for i in iter_list_bins:
            current_bin = i
            #print(current_bin.get_id())
            if largest is None:
                largest = current_bin
            elif largest.get_capacity().compare_to(current_bin.get_capacity()) < 0:
                largest = current_bin
        print("Largest Bin is " + largest.get_id())

    def perform_inverted_allocation(self):
        """ Criticality aware algo """
        all_success = True
        self.populate_criticality_lists()
        
        for i in range(len(self.list_criticalities), 0, -1):
            list_allocated = self.get_all_allocated_elements()
            print(list_allocated)
            self.sort_mfe_by_bandwidth_utilisation(list_allocated, not self.decreasing)

    def populate_criticality_lists(self):
        """ Populate all the msgflow list - criticality wise """
        # Read all the elements in list_elements (contains msgflows

        for msgflow in self.list_elements:
            #print("MSGFLOW: " + msgflow.to_string())
            # Read all the msgflws, check all criticalties
            mfe = msgflow
            mf = mfe.get_message_flow()
            for i in range(0, len(self.list_criticalities)):
                #If criticality exists add it to the list.
                # Ideally, this would be sorting all the criticality of 0, 1, 2 of all flows
                if mf.has_criticality(i):
                    self.list_criticalities[i].append(mfe)

        for i in range(0, len(self.list_criticalities)):
            print("Criticality list " + str(i) + " has ")
            for j in range(0, len(self.list_criticalities[i])):
                print(self.list_criticalities[i][j].get_id())

    def get_all_allocated_elements(self):
        """ Get all allocated items for the network bins """
        allocated_elements = []
        for bins in self.list_bins:
            allocated_elements.extend(bins.get_elements())
        return allocated_elements

    def sort_mfe_by_bandwidth_utilisation(self, list_sort, ascending):
        list_sort.sort(ascending, key=self.myfunc)

    def myfunc(self, mfe):
        return mfe.get_size()



def main():
    """ Testing """
    # Critical level
    flow1 = MessageFlow("1.Flow", 0, 1000, 0.02)
    flow1.set_crit_level(1, 200, 0.01)
    flow1.set_crit_level(2, 100, 0.01)
    flow1.set_crit_level(3, 10, 0.01)

    flow2 = MessageFlow("2.Flow", 0, 500, 0.02)
    flow2.set_crit_level(1, 10, 0.02)
    flow2.set_crit_level(2, 10, 0.05)
    flow2.set_crit_level(3, 10, 0.1)

    flow3 = MessageFlow("3.Flow", 0, 500, 0.02)
    flow3.set_crit_level(1, 10, 0.02)

    flow4 = MessageFlow("4.Flow", 5, 500, 0.02)
    # Let's say network 1 has 8000 bps bandwidth
    network1 = Network("Wi-Fi", True, 8000, -1, -1)
    network2 = Network("SigFox", True, 100, 12, 144)
    network3 = Network("LTE-M", True, 10000, 12, 144)
    network4 = Network("LoRaWAN", True, 11000, 12, 144)
    mnm = multi_network_management()
    mnm.add_msgflow(flow1)
    mnm.add_msgflow(flow2)
    mnm.add_msgflow(flow3)
    mnm.add_msgflow(flow4)
    mnm.add_network(network1)
    mnm.add_network(network2)
    mnm.add_network(network3)
    mnm.add_network(network4)
    bin_t1 = mnm.list_bins[0]
    mfe_t1 = mnm.list_elements[0]
    mfe_t2 = mnm.list_elements[1]
    bin_t1.add_element(mfe_t1)
    bin_t1.add_element(mfe_t2)

    mnm.perform_inverted_allocation()

    # Print the elements
#    for i in mnm.list_elements:
#        print(i.to_string())

#    for i in mnm.list_bins:
#        print i.get_id()
#        print(i.print_allocated())
    mnm.get_largest_bin()

if __name__ == '__main__':
    main()
