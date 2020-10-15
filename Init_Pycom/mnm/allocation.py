""" Allocation Class mainly allocates a msgflow to a network interface """
class Allocation:
    """ Allocation class takes msgflow, network and criticality level """

    def __init__(self, flow, net, crit_level):
        """ Init Function to assign the msgflow, network and criticality
        level """
        self.flow = flow
        self.net = net
        self.crit_level = crit_level

    def get_flow(self):
        """ Return the msgflow instance """
        return self.flow

    def get_network(self):
        """ Return the network instance """
        return self.net

    def get_crit_level(self):
        """ Return the criticality level """
        return self.crit_level

    def to_string(self):
        """ Prints the string which network interface is defined what msgflow
        should be msgflow --> network interface """
        string = self.net.get_name() + " <- " + str(self.get_crit_level()) + " - " + self.flow.get_name()
        # Creating a dict for sending on UART
        dict_alloc = {"MF": self.flow.get_name(), "CL": self.get_crit_level(), "N":self.net.get_name(), "PS": self.flow.get_payload(self.get_crit_level()), "PE": self.flow.get_period(self.get_crit_level())}
        print(string)
        return dict_alloc
