class Network:
    """ Class to define a network interface """
    max_payload = 0
    max_num_msg = 0
    privacy = 0
    name = ""
    bandwidth = 0
    bandwidth_ul = 0
    bandwidth_dl = 0
    available = False

    def __init__(self, name, available, bandwidth, max_payload, max_num_msg):
        self.name = name
        self.available = available
        self.bandwidth = bandwidth
        self.max_payload = max_payload
        self.max_num_msg = max_num_msg

    def get_bandwidth(self):
        return self.bandwidth

    def set_bandwidth(bandwidth):
        self.bandwidth = bandwidth

    def get_available(self):
        return self.available
    
    def set_available(self, available):
        self.available = available

def main():
    network1 = Network("Wi-Fi", True, 80, -1, -1)
    network2 = Network("LoRa", True, 11, 221, 45)
    
    list_net = []
    list_net.append(network1)
    list_net.append(network2)

    for obj in list_net:
        print(obj.name)


if __name__ == '__main__':
    main()

