#!/usr/bin/python

"""UDP interface for Thermometer"""

import os
import SocketServer
import json
import sys
import time
from time import sleep

sleep(60)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

import get_temperature as THERMOMETER
import log_handler
import get_config

CONFIG_FILE_NAME = 'thermometer_config.txt'


class JSONHandler(object):

    """Parse JSON input"""

    def __init__(self, log, probe_location):
        self.logger = log

        #Instantiate Thermometer
        self.thermometer = THERMOMETER.Thermometer(probe_location)

    def __del__(self):
        self.logger.info('Shutting down JSONHandler')

    def shutdown(self):
        self.__del__()

    def __get_settings(self):
        self.logger.debug('Getting status')
        data = self.thermometer.get_temperature()
        self.logger.debug('Received settings')
        return {'TEMPERATURE': data, 'TIME': time.time()}

    def parse(self, command):
        """Handle Set and Get operations"""
        
        self.logger.debug('Received', command)

        try:
            if 'OPERATION' in command or 'OP' in command:

                if command['OPERATION'] == "GET":
                    
                    return json.dumps(self.__get_settings())

            else:
                self.logger.info('Command contains no Operation: %s', command)

        except KeyError:
            self.logger.exception('Key error when parsing %s', command)

        return json.dumps(command)


class UDPHandler(SocketServer.BaseRequestHandler):
    
    """
    UDPHandler to handle UDP requests
    """

    def __init__(self, request, client_address, srvr):
        self.logger = LOGGER1
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, srvr)
        return

    def handle(self):
        data = self.request[0].strip().upper()
        socket = self.request[1]

        self.logger.debug("From %s: %s", self.client_address[0], data)

        try:
            response = JSON_HANDLER.parse(json.loads(data))
            socket.sendto(response, self.client_address)
        except ValueError:
            self.logger.exception('Exception decoding JSON')



if __name__ == "__main__":

    CONFIG = get_config.get_config(CONFIG_FILE_NAME)

    LOG_FILENAME = (THIS_DIR +
                    (lambda: '/' if os.name == 'posix' else '\\')() +
                    CONFIG.get('server', 'logfile'))

    HOST = CONFIG.get('server', 'server_ip')
    PORT = int(CONFIG.get('server', 'server_port'))

    LOGGER1 = log_handler.get_log_handler(LOG_FILENAME, 'debug', 'server.UDPHandler')

    JSON_HANDLER = JSONHandler(log_handler.get_log_handler(LOG_FILENAME,
                                                           'debug',
                                                           'server.JSONParser'),
                               CONFIG.get('thermometer', 'probe')
                              )

    LOGGER1.info('Starting UPD server at %s:%d', HOST, PORT)
    SERVER = SocketServer.UDPServer((HOST, PORT), UDPHandler)
    SERVER.allow_reuse_address = True

    try:
        SERVER.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        JSON_HANDLER.shutdown()
        SERVER.shutdown()
        SERVER.server_close()
        raise

    LOGGER1.info('UDP SocketServer has shutdown')
