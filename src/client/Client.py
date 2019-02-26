from ..client.Session import Session
from ..client.SLA import SLA
import configparser
import rpyc

class Client:

    def __init__(self):
        None

    @staticmethod
    def put(session, key, value):
        # TODO: need to handle errors
        # TODO: This should only go to the main storage node, not the secondaries

        server = Session.connect_to_server()

        server.put(key, value)

    @staticmethod
    def get(session, key, sla=None):
        # Need to maintain a timestamp of storage nodes.
        # Timestamps are used to determine if a node can meet the consistency requirements
        # Need to return the value
        if sla is None:
            sla = session.sla

        value = session.server.get(session.table_name, key)

        return value, None

    @staticmethod
    def create_table(name):
        # TODO: need to deal with possible errors
        server = Session.connect_to_server()

        server.create_table(name)

    @staticmethod
    def delete_table(name):
        # TODO: need to deal with possible errors
        server = Session.connect_to_server()

        server.delete_table(name)

    @staticmethod
    def open_table(name):
        # Return some table object
        #TODO: need to deal with possible errors here
        server = Session.connect_to_server()

        return server.open_table(name)

    @staticmethod
    def begin_session(table_name, sla):
        # Returns some session object
        return Session(table_name, sla)

    @staticmethod
    def end_session(session_object):
        # ends the connection to the table and flushes data
        # TODO: error handling
        session_object.disconnect()


# Implementing session logic
# Needed for read-my-writes, monotonic

if __name__ == "__main__":
    Client.create_table('table1')
    Client.create_table('table2')
    Client.delete_table('table2')
    table = Client.open_table('table1')
    sla = []
    session = Client.begin_session(table, sla)

    key = 'key1'
    value = 1

    Client.put(session, key, value)
    value, cc = Client.get(session, key)

    Client.end_session(session)
