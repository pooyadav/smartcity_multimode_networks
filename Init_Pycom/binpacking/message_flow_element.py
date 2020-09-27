""" MessageFlow Element is just an element which can be assigned to Network Bin"""
# Path hack.
import sys
import os
from doublevaluesize import DoubleValueSize
sys.path.insert(0, os.path.abspath('..'))
from msgflow import MessageFlow

class MessageFlowElement:
    """ Class MessageFlowElement to store msgflow as an Element """

    def __init__(self, msgflow, crit_level):
        """ Defined a msgflow with assigned crit_level """
        self.msgflow = msgflow
        self.allocated_crit_level = crit_level

    def get_message_flow(self):
        """ Return the msgflow """
        return self.msgflow

    def fits_into(self, arg):
        """ Return True if the Msgflow element fits into the Bin?? """
        if self.get_size().compare_to(arg) <= 0:
            return True
        return False

    def get_id(self):
        """ Return the msgflow name """
        return self.msgflow.get_name()

    def get_size(self):
        """ Return the size of the MsgFlow """
        mfe_bandwidth_utilisation = self.msgflow.get_bandwidth_utilisation(self.allocated_crit_level)
        return DoubleValueSize(mfe_bandwidth_utilisation)

    def get_allocated_crit_level(self):
        """ Return the allocated criticality level """
        return self.allocated_crit_level

    def set_allocated_crit_level(self, allocated_crit_level):
        """ Set the allocated criticality level """
        self.allocated_crit_level = allocated_crit_level

    def to_string(self):
        """ ???? """
        return self.msgflow.get_name() + " with criticality level " + str(self.allocated_crit_level) + " with Bandwidth Utilisation of " + str(self.get_size().get_value())
