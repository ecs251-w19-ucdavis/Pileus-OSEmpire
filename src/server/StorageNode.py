import configparser
import signal
import time
import rpyc
from rpyc.utils.server import ThreadedServer
from threading import Thread

import Database
import ReplicationAgent


def terminate_handler():
    print("The StorageNode is terminated")


class StorageNode(rpyc.Service):

    def __init__(self, replicationPortNumber=4001, primary=True):
        self.__isPrimary = primary
        self.__db = Database.Database()
        self.__replicationAgentInstance = ReplicationAgent.ReplicationAgent(primary, self.__db)
        self.__replicationPortNumber = replicationPortNumber
        signal.signal(signal.SIGINT, terminate_handler)
        self.__ReplicationAgentThreadServer = ThreadedServer(self.__replicationAgentInstance, port=self.__replicationPortNumber)
        self.__test = Thread(target=self.__ReplicationAgentThreadServer.start, args=[])
        self.__test.start()

    def __del__(self):
        print('StorageNode: Destructore is called.')
        self.__ReplicationAgentThreadServer.close()

    def on_connect(self, conn):
        '''Not still sure, but maybe if we want to maintain a session information,
        we may need to do something here.'''
        print('StorageNode: connect.')
        # code that runs when a connection is created
        # (to init the service, if needed)
        pass

    def on_disconnect(self, conn):
        print('StorageNode: disconnect.')
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        pass

    def exposed_get_high_timestamp(self):
        result, highTimeStamp = self.__db.get_high_timestamp()
        return highTimeStamp, result

    def exposed_create_table(self, table):
        isSuccesful, resultString = self.__db.create_table(table)
        return isSuccesful, resultString

    def exposed_delete_table(self, table):
        if self.__isPrimary:
            result, resultString = self.__db.delete_table(table)
            return result, resultString
        else:
            resultString = 'StorageNode: Non-primary node cannot delete any table!'
            print('StorageNode: Non-primary node cannot delete any table!')
            return False, resultString

    def exposed_open_table(self, table):
        return self.__db.open_table(table)

    def exposed_get_probe(self):
        result, highTimeStamp = self.__db.get_high_timestamp()
        return highTimeStamp, result

    def exposed_put(self, table, key, value, timestamp):
        high_timestamp = self.__db.get_high_timestamp()
        '''put is callable from client'''
        if self.__isPrimary:
            result, resultString = self.__db.set_item(table, key, value, timestamp)
            return result, resultString, high_timestamp
        else:
            resultString = 'StorageNode: Non-primary node cannot put into table!'
            print('StorageNode: Non-primary node cannot put into table!')
            return False, resultString, high_timestamp

    def exposed_get(self, table, key):
        '''get is callable from client'''
        high_timestamp = self.__db.get_high_timestamp()
        result, resultString = self.__db.get_item(table, key)
        if not result:
            print('StorageNode: Failed to get data from Database!')
            return 0, False, resultString, high_timestamp
        result2, highTimestamp = self.__db.get_high_timestamp()
        if not result2:
            resultString = 'StorageNode: Failed to get high timestamp from Database!'
            print('StorageNode: Failed to get high timestamp from Database!')
            return 0, False, resultString, high_timestamp
        result['high_timestamp'] = highTimestamp
        print(result)
        return result, True, resultString, high_timestamp

    def exposed_get_metadata(self):
        return self.__db.get_metadata()

    def exposed_get_replication_log(self):
        return self.__db.get_replication_log()

    def exposed_get_table(self, table):
        return self.__db.get_table(table)

    def exposed_get_entire_database(self):
        '''get_entire_database is callable from Replication Agent'''
        database = self.__db.get_entire_database()
        return database

    def exposed_is_primary(self):
        '''This is used by replication agent to find whether it is a primary node'''
        return self.__isPrimary

    def exposed_receive_update(self, data):
        result = self.__db.update(data)
        if not result:
            print("Storage Node: Database failed to update the received update!")
        return result

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read_file(open('../../data/Global.conf'))
    portNumber = int(config.get('GeneralConfiguration', 'ClientServerPort'))
    replicationPortNumber = int(config.get('ReplicationAgent', 'ReplicationPort'))

    StorageNodeInstance = StorageNode(replicationPortNumber, primary=False)

    signal.signal(signal.SIGINT, terminate_handler)
    t = ThreadedServer(StorageNodeInstance, port=portNumber)
    t.start()
