import configparser
import rpyc
import time
import threading
import pdb

#In current version, Replication Agent of primary storage does not do anything useful.
#Replication Agents in secondary nodes connect directly to primary storage node, not its replication agent
class ReplicationAgent(rpyc.Service):

    def __init__(self, primary, db):
        config = configparser.ConfigParser()
        config.read_file(open('../../data/Global.conf'))
        storagePortNumber = int(config.get('GeneralConfiguration', 'ClientServerPort'))
        replicationPortNumber = int(config.get('ReplicationAgent', 'ReplicationPort'))
        syncPeriod = int(config.get('ReplicationAgent', 'SyncPeriod'))
        primaryAddress = config.get('Primary', 'IP')
        secondaryAddresses = config.get('Secondary', 'IPs').split(',')

        self.__StoragePortNumber = storagePortNumber
        self.__ReplicationPortNumber = replicationPortNumber
        self.__SyncPeriod = syncPeriod
        self.__isPrimary = primary
        self.__primaryIP = primaryAddress
        self.__secondaryIPes = secondaryAddresses
        self.__StorageDatabaseInstance = db
        self.__UpdateMode = "Log-based"
        # self.__UpdateMode = "Table-based"

        if not self.__isPrimary:
            self.sync()

    def __del__(self):
        print('Replication Agent: Destructore is called.')

    #Used in previous version to see if I'm primary. It has not been used in this version yet.
    def is_primary(self):
        '''Connect to its own StorageNode to see if it is a primary node'''
        is_primary = False
        try:
            connection = rpyc.connect('localhost', port=self.__StoragePortNumber)
            server = connection.root
            is_primary = server.is_primary()
            connection.close()
        except:
            print('Replication Agent: Failed to connect to its own StorageNode!')
        return is_primary

    def send_update(self, destination, port, data):
        try:
            '''Connect to the secondary's replication agent and send data'''
            replicationConnection = rpyc.connect(destination, port=port)
            agent = replicationConnection.root
            agent.receive_update(data)
            replicationConnection.close()
        except:
            print('Replication Agent: There was a problem in sending update to a secondary agent (' + destination + ')!' )

    def exposed_receive_update(self, data):
        if self.__isPrimary:
            print('Replication Agent: Primary agent should not receive update!')
            return False
        try:
            connection = rpyc.connect('localhost', port=self.__StoragePortNumber)
            storageServer = connection.root
            result = storageServer.receive_update(data)
            connection.close()
            if not result:
                print("Replication Agent: StorageNode failed to update the received update!")
                return False
        except:
            print('Replication Agent: Failed to establish a connection or update its storage node!')
            return False
        return True

    def sync(self):
        '''In this version, each secondary check the version of each table and update the
        stale ones periodically'''
        print('Replication Agent: Start updating at ' + str(time.time()) + '.')
        updateMode = self.__UpdateMode
        if not self.__isPrimary:

            if updateMode == "Log-based":
                try:
                    connection = rpyc.connect(self.__primaryIP, port=self.__StoragePortNumber)
                    metadataRetreiveFlag = True
                    storageConnection = connection.root
                    primary_replication_log, result1 = storageConnection.get_replication_log()
                    result2, my_high_timestamp = self.__StorageDatabaseInstance.get_high_timestamp()
                    # print(primary_replication_log, result1)
                    if not result1:
                        print('Replication Agent: Failed to get replication log from Primary Storage Node!')
                        metadataRetreiveFlag = False
                    if not result2:
                        print('Replication Agent: Failed to retrieve its high timestamp!')
                        metadataRetreiveFlag = False

                    if primary_replication_log[0][5] > float(my_high_timestamp):
                        #Cannot relaibly do replication-log-based update. So, switch to table-based update
                        print('Replication Agent: replication.log is newer that my last high timestamp! '
                              'Need to switch back to table-based update.')
                        updateMode = "Table-based"
                    else:
                        if metadataRetreiveFlag:
                            for row in primary_replication_log:
                                if float(row[5]) <= float(my_high_timestamp):
                                    continue
                                try:
                                    if row[0] == 'createTable':
                                        self.__StorageDatabaseInstance.crate_table(row[1], row[5])
                                    elif row[0] == 'deleteTable':
                                        self.__StorageDatabaseInstance.delete_table(row[1], row[5])
                                    elif row[0] == 'put':
                                        self.__StorageDatabaseInstance.set_item_and_high_timestamp(row[1], row[2], row[3], row[4], row[5])
                                except:
                                    print('Replication Agent: Failed to apply update ', row , '! Whole update aborted!')
                                    break
                except:
                    print('Replication Agent: Failed to get data from Primary Storage Node!')

            if updateMode == "Table-based":
                try:
                    connection = rpyc.connect(self.__primaryIP, port=self.__StoragePortNumber)
                    metadataRetreiveFlag = True
                    storageConnection = connection.root
                    primary_metadata, result1 = storageConnection.get_metadata()
                    my_metadata, result2 = self.__StorageDatabaseInstance.get_metadata()
                    print(primary_metadata, result1)
                    if not result1:
                        print('Replication Agent: Failed to get metadata from Primary Storage Node!')
                        metadataRetreiveFlag = False
                    if not result2:
                        print('Replication Agent: Failed to retrieve its metadata!')
                        metadataRetreiveFlag = False

                    if metadataRetreiveFlag:
                        for key in primary_metadata:
                            tableData = storageConnection.get_table(key)
                            if key in my_metadata:
                                #We will update the high timestamp last to make sure it is consistent in worst case
                                if key == '__high_timestamp':
                                    continue
                                if my_metadata[key]['version'] < primary_metadata[key]['version']:
                                    # print(tableData)
                                    result = self.__StorageDatabaseInstance.update_table(key, tableData, primary_metadata[key])
                                    if result:
                                        print('Replication Agent: ' + key + ' table is successfully updated.')
                                else:
                                    print('Replication Agent: ' + key + ' table does not need update.')
                            else:
                                result = self.__StorageDatabaseInstance.update_table(key, tableData, primary_metadata[key])
                                if result:
                                    print('Replication Agent: ' + key + ' table is successfully updated.')
                        #To update the high timestamp
                        key = '__high_timestamp'
                        result = self.__StorageDatabaseInstance.update_high_timestamp(primary_metadata[key]['version'])
                        if result:
                            print('Replication Agent: ' + key + ' table is successfully updated.')
                        else:
                            print('Replication Agent: ' + key + ' table does not need update.')
                except:
                    print('Replication Agent: Failed to get data from Primary Storage Node!')



        threading.Timer(self.__SyncPeriod, self.sync).start()

