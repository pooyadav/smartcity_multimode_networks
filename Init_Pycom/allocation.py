from msgflow import MessageFlow
from network import Network
class Allocation:


    def __init__(self, flow, net, crit_level):
        self.flow = flow
        self.net = net
        self.crit_level = crit_level

    def get_flow():
        return self.msg_flow

    def get_network():
        return self.network

    def get_crit_level(self):
        return self.crit_level

    def to_string(self):
        string = self.net.get_name() + " <- " + str(self.get_crit_level()) + " - " + self.flow.get_name()
        print(string)


def main():

    
    flow1 = MessageFlow("1.Hello", 2, 20, 0.02)
    network1 = Network("Wi-Fi", True, 80, -1, -1)

    all1 = Allocation(flow1, network1, 0)
    all1.to_string()


if __name__ == '__main__':
    main()
