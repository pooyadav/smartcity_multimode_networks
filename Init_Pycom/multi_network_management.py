""" Class to store a list of networks, msgflows and allocations """
from msgflow import MessageFlow
from network_algo import Network
from allocation import Allocation
#from multi_network_management import multi_network_management
from binpacking.message_flow_element import MessageFlowElement
from binpacking.network_bin import NetworkBin
from binpacking.doublevaluesize import DoubleValueSize
from binpacking.exceptions.exceptions import BinFullException, DuplicateElementException

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


    def mf_allocate(self, msgflow, network, critlevel):
        """ Allocate a msgflow of a certain criticality to a network """
        # Deallocate if existing
        self.mf_deallocate(msgflow)
        # Append to the list of allocation
        self.list_allocations.append(Allocation(msgflow, network, critlevel))


    def mf_deallocate(self, msgflow):
        """ De-allocate a msgflow if it is allocated """
        # Find the old allocation
        old_alloc = self.get_allocation_by_msgflow(msgflow)

        # If found, delete it from the list
        if old_alloc is not None:
            print("Old allocation found")
            self.list_allocations.remove(old_alloc)

    def allocate(self, mfe, network):
        """ Allocate the MFE to the network """
        network.add_element(mfe)
        self.mf_allocate(mfe.get_message_flow(), network.get_network(), mfe.get_allocated_crit_level())

    def deallocate(self, mfe):
        """ De-allocate the MFE if it's allocated """
        network = self.get_bin(mfe)
        if network is not None:
            network.remove_element(mfe)
            self.mf_deallocate(mfe.get_message_flow())

    def get_bin(self, mfe):
        """ Return the Network Bin """
        for iter1 in self.list_bins:
            if iter1.contains(mfe):
                return iter1
        return None


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
            #print(msgflow.get_name() + str(msgflow.get_highest_criticality()))
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
#        print("Largest Bin is " + largest.get_id())
        return largest

    def perform_inverted_allocation(self):
        """ Criticality aware algo """
        all_success = True
        ## Populate all the criticalitiy list.
        ## Basically, if we have 5 critical level, we have a list of 5 elements
        # where wach element is another list of MFE of that critical level
        self.populate_criticality_lists()

        # Loop thru all the list of critical levels from High to Low 5 - > 0
        for i in range(len(self.list_criticalities) - 1, -1, -1):
            # Get all the allocated elements from all the network bins
            list_allocated = self.get_all_allocated_elements()

            # Sort the allocated list of MFE by bandwidth utilisation
            self.sort_mfe_by_bandwidth_utilisation(list_allocated, not self.decreasing)

            # Iterating the MFE list of a certain critical level
            iter1 = self.list_criticalities[i]
            for j in iter1:
                temp_msgflow = j.get_message_flow()
                # If the MFE is already allocated remove it from the list
                if self.is_allocated(temp_msgflow):
                    print("Removing " + temp_msgflow.get_name() + " of criticality level " + str(i))
                    self.list_criticalities[i].remove(j)

            # Assigned the MFE elements of a certain critical level
            self.list_elements = self.list_criticalities[i]

            all_success = (self.perform_allocation() or all_success)


        #for i in range(0, len(self.list_criticalities)):
        #    print("New Criticality list " + str(i) + " has ")
        #    for j in range(0, len(self.list_criticalities[i])):
        #        print(self.list_criticalities[i][j].get_id())

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

    def sort_mfe_by_bandwidth_utilisation(self, list_sort, asc_or_dsc):
        """ Sort the list of MFE by bandwidth utilisation """
        list_sort.sort(reverse=asc_or_dsc, key=self.myfunc)
#        print("Sorted List:")
#        for j in list_sort:
#            print(j.to_string())

    def myfunc(self, mfe):
        """ Comparator function for sorting """
        temp = mfe.get_size()
        temp2 = temp.get_value()
        return temp2

    def is_allocated(self, msgflow):
        """ Check if the msgflow is allocated or not
        Calls get_allocation function from Allocation Class """
        current = self.get_allocation(msgflow)
        if current is None:
            return False
        return True

    def get_allocation(self, msgflow):
        """ Return whether the msgflow is allocated or not """

        for i in range(0, len(self.list_allocations)):
            if self.list_allocations[i].get_flow() == msgflow:
                return self.list_allocations[i]
        return None

    def perform_allocation(self):
        """ Perform the allocation of the elements """
        if self.decreasing:
            # Sort the allocated list of MFE by bandwidth utilisation
            self.sort_mfe_by_bandwidth_utilisation(self.list_elements, not self.decreasing)

        for element in self.list_elements:
            self.perform_allocation_step(element)

        # Check if the list of unallocated_elements empty.
        if self.list_unallocated_elements:
            return False
        return True

    def perform_allocation_step(self, element):
        """ Perform the allocation step """

        # Get the largest bin capacity
        bin_capacity = self.get_largest_bin().get_capacity()
        # Check if the elements fits into the Network bin
        if not element.fits_into(bin_capacity):
            print("Element " + element.get_id() + " doesn't fit into Network Bin " + bin_capacity.get_id())
            self.list_unallocated_elements.append(element)
        else:
            current_bin = None
            matching_bin = None
            largest_space = DoubleValueSize(0.0)
            # Start using the largest
            lowest_space = bin_capacity

            # For each existing bin
            for item_bin in self.list_bins:
                current_bin = item_bin
                current_free_space = DoubleValueSize(current_bin.get_free_space())

                # Worst Fit
                if self.worst:
                    # Current Free space is the largest and elements fits the bin
                    if element.fits_into(current_free_space) & current_free_space.compare_to(largest_space) > 0:
                        largest_space = current_free_space
                        matching_bin = current_bin
                # Best Fit
                elif self.best:
                    if element.fits_into(current_free_space) & current_free_space.compare_to(lowest_space) <= 0:
                        lowest_space = current_free_space
                        matching_bin = current_bin
                # First Fit
                elif self.first:
                    if matching_bin is None & element.fits_into(current_free_space):
                        matching_bin = current_bin
                else:
                    if element.fits_into(current_free_space):
                        matching_bin = current_bin

            # Element doesn't fit into any bin
            if ((matching_bin is None) or not element.fits_into(DoubleValueSize(matching_bin.get_free_space()))):
                self.list_unallocated_elements.append(element)
            else:
                try:
                    mfe = element
                    nb = matching_bin
                    print("Trying allocating " + mfe.get_id() + " of criticality level " + str(mfe.get_allocated_crit_level()) + " into " + nb.get_id())
                    self.allocate(mfe, nb)
                    return True

                except BinFullException:
                    print("Network Bin is full")
                    return False
                except DuplicateElementException:
                    print("Duplicate Element")
                    return False

        return False

def main():
    """ Testing """
    # Critical level
    falld = MessageFlow("Fall Detection", 0, 1000, 10)
    falld.set_crit_level(1, 40, 20)
    falld.set_crit_level(2, 10, 60)

    healthm = MessageFlow("Health Monitoring", 0, 1000, 5)
    healthm.set_crit_level(1, 80, 10)
    healthm.set_crit_level(2, 10, 20)

    bodyt = MessageFlow("Body Temperature", 0, 30, 30)
    bodyt.set_crit_level(1, 10, 120)

    bedsens = MessageFlow("Bedroom Sensor", 0, 40000, 10)
    bedsens.set_crit_level(1, 10, 30)

    bathsens = MessageFlow("Bathroom Sensor", 0, 80, 10)
    bathsens.set_crit_level(1, 10, 30)

    kitsens = MessageFlow("Kitchen Sensor", 0, 40000, 10)
    kitsens.set_crit_level(1, 10, 30)

    frontsens = MessageFlow("Front Door Sensor", 0, 40000, 10)
    frontsens.set_crit_level(1, 10, 30)

    enermon = MessageFlow("Energy Usage", 0, 40, 3600)

    # Let's say network 1 has 8000 bps bandwidth
    network1 = Network("Wi-Fi", True, 8000, -1, -1)
    network4 = Network("LoRaWAN", True, 220, 222, 144)
    network2 = Network("SigFox", True, 6, 12, 144)
    network3 = Network("LTE-M", True, 10, 12, 144)
    mnm = multi_network_management()
    mnm.add_msgflow(falld)
    mnm.add_msgflow(healthm)
    mnm.add_msgflow(bodyt)
    mnm.add_msgflow(bedsens)
    mnm.add_msgflow(bathsens)
    mnm.add_msgflow(kitsens)
    mnm.add_msgflow(frontsens)
    mnm.add_msgflow(enermon)
    mnm.add_network(network1)
    mnm.add_network(network4)
    mnm.add_network(network2)
#    mnm.add_network(network3)
#    bin_t1 = mnm.list_bins[0]
#    mfe_t1 = mnm.list_elements[0]
#    mfe_t2 = mnm.list_elements[1]
#    mfe_t3 = mnm.list_elements[2]
#    mfe_t4 = mnm.list_elements[3]
#    mfe_t5 = mnm.list_elements[4]
#    mfe_t6 = mnm.list_elements[5]
#    mfe_t7 = mnm.list_elements[6]
#    mfe_t8 = mnm.list_elements[7]
#    bin_t1.add_element(mfe_t1)
#    mnm.allocate(mfe_t1.get_message_flow(), bin_t1.get_network(), mfe_t1.get_allocated_crit_level())
#    bin_t1.add_element(mfe_t2)
#    bin_t1.add_element(mfe_t3)
#    bin_t1.add_element(mfe_t4)
#    bin_t1.add_element(mfe_t5)
#    bin_t1.add_element(mfe_t6)
#    bin_t1.add_element(mfe_t7)
#    bin_t1.add_element(mfe_t8)

    mnm.perform_inverted_allocation()
    mnm.print_all_allocation()

    # Print the elements
#    for i in mnm.list_elements:
#        print(i.to_string())

#    for i in mnm.list_bins:
#        print i.get_id()
#        print(i.print_allocated())

if __name__ == '__main__':
    main()
