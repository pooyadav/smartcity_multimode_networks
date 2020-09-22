class MessageFlow:
    """ Message Flow Class takes input of criticality, payload size, frequency of messages (period) in seconds?"""
    num_crit_level = 6
    name = ""

    def __init__(self, name, critLevel, payload, period):
        self.name = name
        self.period = [None] * self.num_crit_level
        self.payload = [None] * self.num_crit_level
        self.privacy = [None] * self.num_crit_level
        self.crit_levels = [None] * self.num_crit_level

        for i in range(0, self.num_crit_level):
            self.crit_levels[i] = False

#        self.name[critLevel] = name
        self.period[critLevel] = period
        self.payload[critLevel] = payload
        self.crit_levels[critLevel] = True

    def set_crit_level(self, critLevel, payload, period):
        """ Set Criticality level of a message flow """
        self.period[critLevel] = period
        self.payload[critLevel] = payload
        self.crit_levels[critLevel] = True

    def get_period(self, critLevel):
        """ Return the time period for a given Criticality level """
        if(self.crit_levels[critLevel]):
            return self.period[critLevel]
        else:
            return -1

    def get_payload(self, critLevel):
        """ Return the Payload Size for a given Criticality level """
        if(self.crit_levels[critLevel]):
            return self.payload[critLevel]
        else:
            return -1

    def get_bandwidth(self, critLevel):
        """ Return bandwidth required for a given Criticality level """
        return self.get_payload(critLevel)/self.get_period(critLevel)

    def printAll(self):
        print(self.name)
        print(self.payload)
        print(self.period)
#        print(self.privacy)
        print(self.crit_levels)

def main():
    flow1 = MessageFlow("1.Hello", 2, 20, 0.02)
    flow2 = MessageFlow("2.Hello", 2, 20, 0.02)
    flow1.set_crit_level(1, 10, 0.03)
    flow1.set_crit_level(1, 20, 0.01);
    flow1.set_crit_level(0, 80, 0.01);
    flow1.set_crit_level(3, 10, 0.02);
    flow1.set_crit_level(4, 10, 0.05);
    flow1.set_crit_level(5, 10, 0.1);
    print(flow1.get_payload(2))
    print(flow1.get_period(2))
    print(flow1.get_bandwidth(2))
    flow1.printAll()

    list_num = []
    list_num.append(flow1)
    list_num.append(flow2)
    
    for obj in list_num:
        print(obj.name)


if __name__ == '__main__':
    main()

