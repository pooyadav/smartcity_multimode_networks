""" DoubleValueSize Class Not sure why not working :X"""
class DoubleValueSize:
    def __init__(self, value):
        self.value = value

    def compare_to(self,other):
        """ Compares this DoubleValueSize's double value against another's double value
        @return -1 if this double value is smaller than other's double value
                 1 if this double value is larger than other's double value
                 0 if this double value is equal to than other's double value """
        if self.get_value() < other.get_value():
            return -1
        if self.get_value() > other.get_value():
            return 1
        return 0

    def get_value(self):
        """ Return the value """
        return self.value

    def to_string(self):
        """ Return the string of the value """
        return str(self.value)

    def add(self, other):
        other_value = other.get_value()
        result_sum = self.value + other_value
        return result_sum

    def subtract(self, other):
        other_value = other.get_value()
        return self.value - other_value

    def calculate_percentage(self, other):
        return other.get_value()/self.value
