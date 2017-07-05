#!/usr/bin/env python

"""Return reading from temperature probe"""

import re
import os
from time import sleep


class Thermometer(object):

    """Temperature object"""

    def __init__(self, temp_location):
        self.probe_file = temp_location

        while not os.path.isfile(self.probe_file):
            sleep(5)

    def get_temperature(self):

        """
        parse file which stores temperature reading
        return temp in Celcius
        """

        probe_file = open(self.probe_file, 'r')
        probe_data = probe_file.readlines()
        probe_data = probe_data[1]
        extract = re.search('t=(.+?)\n', probe_data)
        temperature = extract.group(1)
        return float(temperature)/1000

    def set_probe_file(self, temp_location):
        """Set file location of temp probe data"""
        self.probe_file = temp_location


if __name__ == "__main__":

    THERMO = Thermometer('/sys/bus/w1/devices/28-000007662891/w1_slave')

    print THERMO.get_temperature()
