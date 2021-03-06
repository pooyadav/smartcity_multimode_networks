""" MessageFlow Class to define a message flow from the application """
class MessageFlow:
    """ Message Flow Class takes input of criticality, payload size,
    frequency of messages (period) in seconds?"""
    num_crit_level = 6
    name = ""

    def __init__(self, name, crit_level, payload, period):
        """ Init function to create a array (list) of payload size,
        period, privacy and crit_levels of num_crit_level size """
        self.name = name
        self.period = [None] * self.num_crit_level
        self.payload = [None] * self.num_crit_level
        self.privacy = [None] * self.num_crit_level
        self.crit_levels = [None] * self.num_crit_level

        for i in range(0, self.num_crit_level):
            self.crit_levels[i] = False

#        self.name[crit_level] = name
        self.period[crit_level] = period
        self.payload[crit_level] = payload
        self.crit_levels[crit_level] = True

    def set_crit_level(self, crit_level, payload, period):
        """ Set Criticality level of a message flow """
        self.period[crit_level] = period
        self.payload[crit_level] = payload
        self.crit_levels[crit_level] = True

    def get_name(self):
        """ Return the name of the MessageFlow """
        return self.name

    def get_period(self, crit_level):
        """ Return the time period for a given Criticality level """
        if self.crit_levels[crit_level]:
            return self.period[crit_level]
        else:
            return -1

    def get_payload(self, crit_level):
        """ Return the Payload Size for a given Criticality level """
        if self.crit_levels[crit_level]:
            return self.payload[crit_level]
        else:
            return -1

    def get_bandwidth(self, crit_level):
        """ Return bandwidth required for a given Criticality level """
        return self.get_payload(crit_level)/self.get_period(crit_level)

    def get_highest_criticality(self):
        """ Return the highest criticality defined in msgflow """
        for i in range(len(self.crit_levels), 0, -1):
            if self.crit_levels[i-1]:
                return i - 1
        return -1

    def get_lowest_criticality(self):
        """ Return the lowest criticality defined in msgflow """
        for i in range(0, len(self.crit_levels), 1):
            if self.crit_levels[i]:
                return i
        return -1

    def print_all_msgflows(self):
        """ Print all the msgflows """
        print(self.name)
        print(self.payload)
        print(self.period)
#        print(self.privacy)
        print(self.crit_levels)

    def get_bandwidth_utilisation(self, crit_level):
        """ Return bandwidth utilisation """
        payload = self.get_payload(crit_level)
        period = self.get_period(crit_level)
        bandwidth_util = float(payload)/float(period)
        return bandwidth_util

    def has_criticality(self, i):
        """ Return whether a particular criticality level has been set """
        return self.crit_levels[i]
