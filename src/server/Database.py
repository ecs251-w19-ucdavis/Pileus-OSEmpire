import json
import configparser
import os
import time
import csv
from src.server import ReadWriteLock
import threading
from threading import Thread

#MetaData table contains status and version of all tables
#Metadata Status: 0->Created, 1 -> Changed, 2->Deleted

class Database:
    key_string_error = TypeError('Key/name must be a string!')

    def __init__(self):
        self.__replication_log_rwlock = ReadWriteLock.ReadWriteLock()
        self.__metadata_rwlock = ReadWriteLock.ReadWriteLock()
        self.__table_rwlock = ReadWriteLock.ReadWriteLock()
        self.__lock = threading.Lock()

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
            self.update_high_timestamp('0.00001')

        self.__replicationLogTable = self.__path + 'replication.log'
        if not os.path.exists(self.__replicationLogTable):
            # To create an empty replication.log file
            with open(self.__replicationLogTable, "w", newline='') as empty_csv:
                em_csv = csv.writer(empty_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                pass

    def update_replication_log(self, Operation, tableName, key, value, timestamp, high_timestamp):
        try:
            self.__replication_log_rwlock.acquire_write()
            row = [Operation, tableName, key, value, timestamp, high_timestamp]
            with open(self.__replicationLogTable, 'a', newline='') as fd:
                csv_writer = csv.writer(fd, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                csv_writer.writerow(row)
            print('Database: Row was succesfully added to the replication.log.')
            self.__replication_log_rwlock.release_write()
            return True
        except:
            print('Database: Failed to update replication.log!')
            self.__replication_log_rwlock.release_write()
            return False

    def clear_entire_replication_log(self):
        # To create an empty replication.log file
        self.__replication_log_rwlock.acquire_write()
        with open(self.__replicationLogTable, "w", newline='') as empty_csv:
            em_csv = csv.writer(empty_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            pass
        self.__replication_log_rwlock.release_write()

    #Remove replication records that was commited before last ReplicationLogCleaningPeriod
    def remove_old_replication_records(self, ReplicationLogCleaningPeriod):
        result, highTimeStamp = self.get_high_timestamp()
        if not result:
            return False
        try:
            self.__replication_log_rwlock.acquire_write()
            with open(self.__replicationLogTable, "r") as inp:
                rows = list(csv.reader(inp))
                with open(self.__replicationLogTable + '.temp', 'w', newline='') as out:
                    writer = csv.writer(out, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                    for row in rows:
                        if float(row[5]) >= highTimeStamp - float(ReplicationLogCleaningPeriod):
                            writer.writerow(row)
            os.remove(self.__replicationLogTable)
            os.rename(self.__replicationLogTable + '.temp', self.__replicationLogTable)
        except:
            print('Database: Failed to remove old replication records!')
        self.__replication_log_rwlock.release_write()


    def update_metadata(self, table, status, version='-1'):
        try:
            self.__metadata_rwlock.acquire_write()
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
            self.__metadata_rwlock.release_write()
            return True
        except:
            print('Database: Failed to update MetaData.')
            self.__metadata_rwlock.release_write()
            return False

    def update_high_timestamp(self, newHighTimestamp='0'):
        table = '__high_timestamp'
        try:
            self.__metadata_rwlock.acquire_write()
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
            self.__metadata_rwlock.release_write()
            return True, newTime
        except:
            print('Database: Failed to update high timestamp.')
            self.__metadata_rwlock.release_write()
            return False, 0

    def get_high_timestamp(self):
        table = '__high_timestamp'
        try:
            self.__metadata_rwlock.acquire_read()
            with open(self.__metaTable, 'r') as fd:
                db = json.load(fd)
                if table in db:
                    highTimestamp = float(db[table]['version'])
                else:
                    print('Database: No __high_timestamp metadata available!')
                    self.__metadata_rwlock.release_read()
                    return False, 0
            self.__metadata_rwlock.release_read()
            return True, highTimestamp
        except:
            print('Database: Failed to return high timestamp.')
            self.__metadata_rwlock.release_read()
            return False, 0

    def get_metadata(self):
        db = {}
        try:
            self.__metadata_rwlock.acquire_read()
            with open(self.__metaTable, 'r') as fd:
                db = json.load(fd)
            self.__metadata_rwlock.release_read()
        except:
            print('Database: Failed to open MetaData.')
            self.__metadata_rwlock.release_read()
            return db, False
        self.__metadata_rwlock.release_read()
        return db, True

    def get_replication_log(self):
        replicationLog = []
        try:
            self.__replication_log_rwlock.acquire_read()
            with open(self.__replicationLogTable, 'r', newline='') as fd:
                replicationLog = list(csv.reader(fd))
            print(replicationLog)
        except:
            print('Database: Failed to open Replication.log!')
            self.__replication_log_rwlock.release_read()
            return replicationLog, False
        self.__replication_log_rwlock.release_read()
        return replicationLog, True

    def create_table(self, tableName, highTimestamp='0'):
        resultString = ''
        table = self.__path + tableName + '.json'
        if os.path.exists(table):
            resultString = 'Database: The table already exist!'
            print('Database: The table already exist!')
            return False, resultString
        else:
            with self.__lock:
                try:
                    result, newHighTimeStamp = self.update_high_timestamp(highTimestamp)
                    if not result:
                        resultString = 'Database: Failed to update high timestamp table! Entire update was aborted.'
                        print('Database: Failed to update high timestamp table! Entire update was aborted.')
                        return False, resultString
                except:
                    resultString = 'Database: Failed to update high timestamp table! Entire update was aborted.'
                    print('Database: Failed to update high timestamp table! Entire update was aborted.')
                    return False, resultString
                try:
                    db = {}
                    result = self.dump(table, db)
                    if not result:
                        resultString = 'Database: Failed to create ' + tableName + ' table!'
                        print('Database: Failed to create ' + tableName + ' table!')
                        return False, resultString
                    result = self.update_metadata(tableName, '0')
                    if not result:
                        #If it cannot update metadata, it will undo the table creation
                        self.delete_table(table)
                        resultString = 'Database: Failed to create ' + tableName + ' table!'
                        print('Database: Failed to create ' + tableName + ' table!')
                        return False, resultString
                    resultString = 'Database: ' + tableName + ' table was successfully created.'
                    print('Database: ' + tableName + ' table was successfully created.')
                except:
                    resultString = 'Database: Failed to create ' + tableName + ' table!'
                    print('Database: Failed to create ' + tableName + ' table!')
                    return False, resultString

                try:
                    self.update_replication_log( "createTable", tableName, "", "", "", newHighTimeStamp)
                    resultString = 'Database: Update was successfully added to replication.log.'
                    print('Database: Update was successfully added to replication.log.')
                    return True, resultString
                except:
                    resultString = 'Database: Failed to added update to replication.log!'
                    print('Database: Failed to added update to replication.log!')
                    return False, resultString


    def delete_table(self, tableName, highTimestamp='0'):
        table = self.__path + tableName + '.json'
        with self.__lock:
            if os.path.exists(table):
                try:
                    result, newHighTimeStamp = self.update_high_timestamp(highTimestamp)
                    if not result:
                        resultString = 'Database: Failed to update high timestamp table! Entire update was aborted.'
                        print('Database: Failed to update high timestamp table! Entire update was aborted.')
                        return False, resultString
                except:
                    resultString = 'Database: Failed to update high timestamp table! Entire update was aborted.'
                    print('Database: Failed to update high timestamp table! Entire update was aborted.')
                    return False, resultString
                try:
                    os.remove(table)
                    self.update_metadata(tableName, '2')
                    print('Database: Metadata was successfully updated.')
                except:
                    resultString = 'Database: Failed to delete ' + tableName + ' table!'
                    print('Database: Failed to delete ' + tableName + ' table!')
                    return False, resultString

                try:
                    self.update_replication_log("deleteTable", tableName, "", "", "", newHighTimeStamp)
                    resultString = 'Database: ' + tableName + ' table was successfully deleted.'
                    print('Database: ' + tableName + ' table was successfully deleted.')
                    return True, resultString
                except:
                    resultString = 'Database: Failed to added update to replication.log!'
                    print('Database: Failed to added update to replication.log!')
                    return False, resultString
            else:
                resultString = 'Database: ' + tableName + ' table does not exist!'
                print('Database: ' + tableName + ' table does not exist!')
                return False, resultString

    def open_table(self):
        return True

    def get_table(self, tableName):
        table = self.__path + tableName + '.json'
        self.__table_rwlock.acquire_read()
        if os.path.exists(table):
            try:
                tbl = {}
                with open(table, 'r') as fd:
                    tbl = json.load(fd)
                self.__table_rwlock.release_read()
                return tbl
            except:
                print('Database: Failed to get ' + tableName + ' table (Maybe locked)!')
                self.__table_rwlock.release_read()
                return False
        else:
            print('Database: ' + tableName + ' table does not exist!')
            self.__table_rwlock.release_read()
            return False

    def update_table(self, tableName, tableData, value):
        with self.__lock:
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

                self.__table_rwlock.acquire_write()
                result = self.dump(table, copiedTable)
                self.__table_rwlock.release_write()
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
        with self.__lock:
            if os.path.exists(table):
                try:
                    result, newHighTimeStamp = self.update_high_timestamp()
                    if not result:
                        resultString = 'Database: Failed to update high timestamp table! Entire update was aborted.'
                        print('Database: Failed to update high timestamp table! Entire update was aborted.')
                        return False, resultString
                except:
                    resultString = 'Database: Failed to update high timestamp table! Entire update was aborted.'
                    print('Database: Failed to update high timestamp table! Entire update was aborted.')
                    return False, resultString
                try:
                    self.__table_rwlock.acquire_write()
                    with open(table, 'r') as fd:
                        db = json.load(fd)
                        if key in db:
                            if float(timestamp) <= float(db[key]['timestamp']):
                                resultString = 'Database: The new timestamp is older than the existing one!'
                                print('Database: The new timestamp is older than the existing one!')
                                self.__table_rwlock.release_write()
                                return False, resultString
                    db[key] = {'value': value, 'timestamp': timestamp}
                    self.dump(table, db)
                    print('Database: ' + key + ' key was successfully added to ' + tableName + ' table.')
                    self.__table_rwlock.release_write()
                except:
                    resultString = 'Database: Failed to put data into ' + tableName + ' table!'
                    print('Database: Failed to put data into ' + tableName + ' table!')
                    self.__table_rwlock.release_write()
                    return False, resultString

                try:
                    self.update_metadata(tableName, '1')
                    print('Database: Metadata was successfully updated.')
                except:
                    resultString = 'Database: Files to update Metadata.'
                    print('Database: Files to update Metadata.')
                    return False, resultString

                try:
                    self.update_replication_log("put", tableName, key, value, timestamp, newHighTimeStamp)
                    print('Database: Update was successfully added to replication.log.')
                    resultString = 'Database: Uppdate was successful.'
                    return True, resultString
                except:
                    resultString = 'Database: Failed to added update to replication.log!'
                    print('Database: Failed to added update to replication.log!')
                    return False, resultString
            else:
                resultString = 'Database: ' + tableName + ' table does not exist!'
                print('Database: ' + tableName + ' table does not exist!')
                return False, resultString

    #It is used by secondary nodes when they receive replication log from primary yo apply updates
    def set_item_and_high_timestamp(self, tableName, key, value, timestamp, newHighTimeStamp):
        table = self.__path + tableName + '.json'
        with self.__lock:
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
                    self.__table_rwlock.acquire_write()
                    with open(table, 'r') as fd:
                        db = json.load(fd)
                    db[key] = {'value': value, 'timestamp': timestamp}
                    self.dump(table, db)
                    print('Database: ' + key + ' key was successfully added to ' + tableName + ' table.')
                    self.__table_rwlock.release_write()
                except:
                    print('Database: Failed to put data into ' + tableName + ' table!')
                    self.__table_rwlock.release_write()
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
            self.__table_rwlock.acquire_read()
            try:
                with open(table) as fd:
                    db = json.load(fd)
                    if key in db:
                        value = db[key]
                    else:
                        resultString = 'Database: ' + key + ' key does not exist in  ' + tableName + ' table!'
                        print('Database: ' + key + ' key does not exist in  ' + tableName + ' table!')
                        self.__table_rwlock.release_read()
                        return False, resultString
                self.__table_rwlock.release_read()
                resultString = 'Database: Get was successful.'
                return value, resultString
            except:
                resultString = 'Database: Failed to get data from ' + tableName + ' table!'
                print('Database: Failed to get data from ' + tableName + ' table!')
                self.__table_rwlock.release_read()
                return False, resultString
        else:
            resultString = 'Database: ' + tableName + ' table does not exist!'
            print('Database: ' + tableName + ' table does not exist!')
            return False, resultString


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
    # for b in t:
    #     print(b)
    # print(t)
    # print(t[0][1])
    a.remove_old_replication_records(20)
    del a
