import json
import configparser
import os
from threading import Thread


class Database:
    key_string_error = TypeError('Key/name must be a string!')

    def __init__(self):
        config = configparser.ConfigParser()
        config.read_file(open('Global.conf'))
        self.file = config.get('Database', 'file')
        print(self.file)

        if os.path.exists(self.file):
            self.db = json.load(open(self.file, 'rt'))
        else:
            '''Create an empty database. It will be saved to disk when a data is entered.'''
            self.db = {}

    def set_item(self, key, value, timestamp):
        '''Set the str value of a key'''
        try:
            self.db[key] = {'value': value, 'timestamp': timestamp}
            self.dump()
            return True
        except KeyError:
            return False

    def get_item(self, key):
        try:
            return self.db[key]
        except KeyError:
            return False

    def dump(self):
        '''Dump memory db to file'''
        json.dump(self.db, open(self.file, 'wt'))
        # self.dthread = Thread(
        #     target=json.dump,
        #     args=(self.db, open(self.file, 'wt')))
        # self.dthread.start()
        # self.dthread.join()
        return True


if __name__ == "__main__":
    a = Database()
    a.set_item('1','ewsdfd','12')
    a.set_item('2','asda','4')
    print(a.get_item('2'))
    del a
