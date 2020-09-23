from msgflow import MessageFlow
from network_algo import Network
from allocation import Allocation

class MultiNetworkManagement():
    list_networks = []
    list_msgflows = []
    list_allocations = []

    def allocate(self, msgflow, network, critlevel):
        # Deallocate if existing
        self.deallocate(msgflow)
        # Append to the list of allocation
        self.list_allocations.append(Allocation(msgflow, network, critlevel))


    def deallocate(self,msgflow):
        # Find the old allocation
        old_alloc = self.get_allocation_by_msgflow(msgflow)

        # If found, delete it from the list
        if (old_alloc!= None):
	    print("Old allocation found")
            self.list_allocations.remove(old_alloc)


    def get_allocation_by_msgflow(self, msgflow):
        for i in self.list_allocations:
            if(i.get_flow() == msgflow):
                return i
        return None

    def print_all_allocation(self):
        for i in self.list_allocations:
            i.to_string()

def main():


    flow1 = MessageFlow("1.Hello", 2, 20, 0.02)
    flow2 = MessageFlow("2.Hello", 2, 20, 0.02)
    network1 = Network("Wi-Fi", True, 80, -1, -1)
    mnm = MultiNetworkManagement()

    all1 = mnm.allocate(flow1, network1, 0)
    all2 = mnm.allocate(flow2, network1, 0)
    mnm.print_all_allocation()


if __name__ == '__main__':
    main()
