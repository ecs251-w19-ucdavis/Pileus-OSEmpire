import json
import configparser
import os
import time
import csv
from threading import Thread

#MetaData table contains status and version of all tables
#Metadata Status: 0->Created, 1 -> Changed, 2->Deleted

class Database:
    key_string_error = TypeError('Key/name must be a string!')

    def __init__(self):
        config = configparser.ConfigParser()
        config.read_file(open('../../data/Global.conf'))
        self.__path = '../..' + config.get('Database', 'Path')
        print(self.__path)

        if not os.path.exists(self.__path):
            os.makedirs(self.__path)
            # self.db = json.load(open(self.file, 'rt'))

        self.__metaTable = self.__path + 'metadata.meta'
        if not os.path.exists(self.__metaTable):
            db = {}
            self.dump(self.__metaTable, db)
            self.update_high_timestamp()

        self.__replicationLogTable = self.__path + 'replication.log'
        if not os.path.exists(self.__replicationLogTable):
            # To create an empty replication.log file
            with open(self.__replicationLogTable, "w", newline='') as empty_csv:
                em_csv = csv.writer(empty_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                pass

    def update_replication_log(self, Operation, tableName, key, value, timestamp, high_timestamp):
        try:
            row = [Operation, tableName, key, value, timestamp, high_timestamp]
            with open(self.__replicationLogTable, 'a', newline='') as fd:
                csv_writer = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                csv_writer.writerow(row)
            print('Database: Row was succesfully added to the replication.log.')
            return True
        except:
            print('Database: Failed to update replication.log!')
            return False

    def update_metadata(self, table, status, version='-1'):
        try:
            newVersion = 0
            with open(self.__metaTable, 'r') as fd:
                db = json.load(fd)
                if table in db:
                    newVersion = float(db[table]['version']) + 1
                if not version=='-1':
                    newVersion = version

            db[table] = {'version': newVersion, 'status': status}
            self.dump(self.__metaTable, db)
            print('Database: MetaData was successfully updated.')
            return True
        except:
            print('Database: Failed to update MetaData.')
            return False

    def update_high_timestamp(self, newHighTimestamp='0'):
        table = '__high_timestamp'
        try:
            with open(self.__metaTable, 'r') as fd:
                db = json.load(fd)
            if newHighTimestamp == '0':
                # used when a primary node wants to update the local high timestamp
                newTime = str(time.time())
            else:
                #used when a secondary node wants to update the high timestamp
                newTime = newHighTimestamp

            db[table] = {'version': newTime, 'status': '1'}
            self.dump(self.__metaTable, db)
            print('Database: High timestamp was successfully updated.')
            return True, newTime
        except:
            print('Database: Failed to update high timestamp.')
            return False, 0

    def get_high_timestamp(self):
        table = '__high_timestamp'
        try:
            with open(self.__metaTable, 'r') as fd:
                db = json.load(fd)
                if table in db:
                    highTimestamp = float(db[table]['version'])
                else:
                    print('Database: No __high_timestamp metadata available!')
                    return False, 0
            return True, highTimestamp
        except:
            print('Database: Failed to return high timestamp.')
            return False, 0

    def get_metadata(self):
        db = {}
        try:
            with open(self.__metaTable, 'r') as fd:
                db = json.load(fd)
        except:
            print('Database: Failed to open MetaData.')
            return db, False
        return db, True

    def get_replication_log(self):
        replicationLog = []
        try:
            with open(self.__replicationLogTable, 'r', newline='') as fd:
                replicationLog = list(csv.reader(fd))
            print(replicationLog)
        except:
            print('Database: Failed to open Replication.log!')
            return replicationLog, False
        return replicationLog, True

    def create_table(self, tableName, highTimestamp='0'):
        table = self.__path + tableName + '.json'
        if os.path.exists(table):
            print('Database: The table already exist!')
            return False
        else:
            try:
                result, newHighTimeStamp = self.update_high_timestamp(highTimestamp)
                if not result:
                    print('Database: Failed to update high timestamp table! Entire update was aborted.')
                    return False
            except:
                print('Database: Failed to update high timestamp table! Entire update was aborted.')
                return False
            try:
                db = {}
                result = self.dump(table, db)
                if not result:
                    print('Database: Failed to create ' + tableName + ' table!')
                    return False
                result = self.update_metadata(tableName, '0')
                if not result:
                    #If it cannot update metadata, it will undo the table creation
                    self.delete_table(table)
                    print('Database: Failed to create ' + tableName + ' table!')
                    return False
                print('Database: ' + tableName + ' table was successfully created.')
            except:
                print('Database: Failed to create ' + tableName + ' table!')
                return False

            try:
                self.update_replication_log( "createTable", tableName, "", "", "", newHighTimeStamp)
                print('Database: Update was successfully added to replication.log.')
                return True
            except:
                print('Database: Failed to added update to replication.log!')
                return False


    def delete_table(self, tableName, highTimestamp='0'):
        table = self.__path + tableName + '.json'
        if os.path.exists(table):
            try:
                result, newHighTimeStamp = self.update_high_timestamp(highTimestamp)
                if not result:
                    print('Database: Failed to update high timestamp table! Entire update was aborted.')
                    return False
            except:
                print('Database: Failed to update high timestamp table! Entire update was aborted.')
                return False
            try:
                os.remove(table)
                self.update_metadata(tableName, '2')
                print('Database: ' + tableName + ' table was successfully deleted.')
            except:
                print('Database: Failed to delete ' + tableName + ' table!')
                return False

            try:
                self.update_replication_log("deleteTable", tableName, "", "", "", newHighTimeStamp)
                print('Database: ' + tableName + ' table was successfully deleted.')
                return True
            except:
                print('Database: Failed to added update to replication.log!')
                return False
        else:
            print('Database: ' + tableName + ' table does not exist!')
            return False

    def open_table(self):
        return True

    def get_table(self, tableName):
        table = self.__path + tableName + '.json'
        if os.path.exists(table):
            try:
                tbl = {}
                with open(table, 'r') as fd:
                    tbl = json.load(fd)
                return tbl
            except:
                print('Database: Failed to get ' + tableName + ' table (Maybe locked)!')
                return False
        else:
            print('Database: ' + tableName + ' table does not exist!')
            return False

    def update_table(self, tableName, tableData, value):
        table = self.__path + tableName + '.json'
        backupTable = {}
        if os.path.exists(table):
            backupTable = self.get_table(tableName)
        print(tableData)
        status = value['status']
        if status == '0':
            result = self.create_table(tableName)
        elif status == '1':

            #cannot work with netref object, I need to copy that first
            copiedTable = {}
            for k in tableData:
                temp = {}
                temp['timestamp'] = tableData[k]['timestamp']
                temp['value'] = tableData[k]['value']
                copiedTable[k] = temp

            result = self.dump(table, copiedTable)
            if not result:
                return False
            result = self.update_metadata(tableName, value['status'], value['version'])
            if not result:
                #If couldn't update both table and metadata, it will restore the table to previous version
                self.dump(tableName, backupTable)
        elif status == '2':
            result = self.delete_table(tableName)
        if not result:
            return False


    def set_item(self, tableName, key, value, timestamp):
        table = self.__path + tableName + '.json'
        if os.path.exists(table):
            try:
                result, newHighTimeStamp = self.update_high_timestamp()
                if not result:
                    print('Database: Failed to update high timestamp table! Entire update was aborted.')
                    return False
            except:
                print('Database: Failed to update high timestamp table! Entire update was aborted.')
                return False
            try:
                with open(table, 'r') as fd:
                    db = json.load(fd)
                    if key in db:
                        if float(timestamp) <= float(db[key]['timestamp']):
                            print('Database: The new timestamp is older than the existing one!')
                            return False
                db[key] = {'value': value, 'timestamp': timestamp}
                self.dump(table, db)
                print('Database: ' + key + ' key was successfully added to ' + tableName + ' table.')
            except:
                print('Database: Failed to put data into ' + tableName + ' table!')
                return False

            try:
                self.update_metadata(tableName, '1')
                print('Database: Metadata was successfully updated.')
            except:
                print('Database: Files to update Metadata.')
                return False

            try:
                self.update_replication_log("put", tableName, key, value, timestamp, newHighTimeStamp)
                print('Database: Update was successfully added to replication.log.')
                return True
            except:
                print('Database: Failed to added update to replication.log!')
                return False
        else:
            print('Database: ' + tableName + ' table does not exist!')
            return False

    #It is used by secondary nodes when they receive replication log from primary yo apply updates
    def set_item_and_high_timestamp(self, tableName, key, value, timestamp, newHighTimeStamp):
        table = self.__path + tableName + '.json'
        if os.path.exists(table):
            try:
                result, newHighTimeStamp = self.update_high_timestamp(newHighTimeStamp)
                if not result:
                    print('Database: Failed to update high timestamp table! Entire update was aborted.')
                    return False
            except:
                print('Database: Failed to update high timestamp table! Entire update was aborted.')
                return False
            try:
                with open(table, 'r') as fd:
                    db = json.load(fd)
                db[key] = {'value': value, 'timestamp': timestamp}
                self.dump(table, db)
                print('Database: ' + key + ' key was successfully added to ' + tableName + ' table.')
            except:
                print('Database: Failed to put data into ' + tableName + ' table!')
                return False

            try:
                self.update_metadata(tableName, '1')
                print('Database: Metadata was successfully updated.')
            except:
                print('Database: Files to update Metadata.')
                return False

            try:
                self.update_replication_log("put", tableName, key, value, timestamp, newHighTimeStamp)
                print('Database: Update was successfully added to replication.log.')
                return True
            except:
                print('Database: Failed to added update to replication.log!')
                return False
        else:
            print('Database: ' + tableName + ' table does not exist!')
            return False

    def get_item(self, tableName, key):
        table = self.__path + tableName + '.json'
        if os.path.exists(table):
            try:
                with open(table) as fd:
                    db = json.load(fd)
                    if key in db:
                        value = db[key]
                    else:
                        print('Database: ' + key + ' key does not exist in  ' + tableName + ' table!')
                        return False
                return value
            except:
                print('Database: Failed to get data from ' + tableName + ' table!')
                return False
        else:
            print('Database: ' + tableName + ' table does not exist!')
            return False


    def dump(self, tableName, database):
        '''Dump memory db to file'''
        try:
            json.dump(database, open(tableName, 'wt'))
            # self.dthread = Thread(
            #     target=json.dump,
            #     args=(self.db, open(self.file, 'wt')))
            # self.dthread.start()
            # self.dthread.join()
        except:
            print('Database: Failed to dump database into file!')
            return False
        return True


if __name__ == "__main__":
    a = Database()
    a.create_table('sha')
    a.create_table('te')
    a.set_item('sha', '1', 'ewsdfd', '12')
    a.set_item('sha', '2', 'asda', '3.5')
    a.set_item('sdfe','r','ere','r')
    a.delete_table("te")
    print(a.get_item('sha','2'))
    print(a.get_item('shad', '2'))
    print(a.get_item('sha', '3'))
    t, result = a.get_replication_log()
    for b in t:
        print(b)
    # print(t)
    # print(t[0][1])
    del a
