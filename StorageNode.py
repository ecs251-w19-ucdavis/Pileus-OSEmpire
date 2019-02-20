import os
import pdb
import configparser
import Database
import rpyc
import threading
import signal
from rpyc.utils.server import ThreadedServer


def terminate_handler():
    print("The StorageNode is terminated")


class StorageNode(rpyc.Service):

    def __init__(self):
        self.__isPrimary = True
        self.__db = Database.Database()

    def on_connect(self, conn):
        '''Not still sure, but maybe if we want to maintain a session information,
        we may need to do something here.'''
        # code that runs when a connection is created
        # (to init the service, if needed)
        pass

    def on_disconnect(self, conn):
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        pass

    def exposed_put(self, key, value, timestamp):
        '''put is callable from client'''
        result = self.__db.set_item(key, value, timestamp)
        return result

    def exposed_get(self, key):
        '''get is callable from client'''
        result = self.__db.get_item(key)
        return result


if __name__ == "__main__":
    test = StorageNode()

    config = configparser.ConfigParser()
    config.read_file(open('Global.conf'))
    portNumber = int(config.get('GeneralConfiguration', 'ClientServerPort'))
    print(portNumber)

    signal.signal(signal.SIGINT, terminate_handler)
    t = ThreadedServer(StorageNode, port=portNumber)
    t.start()
