from ..client.Session import Session
from ..client.SLA import SLA
from ..client.Monitor import Monitor
import time
import configparser

class Client:

    def __init__(self, monitor, config_file_path):
        self.monitor = monitor
        self.config_file_path = config_file_path
        self.config = configparser.ConfigParser()
        with open(config_file_path, 'r') as read_file:
            self.config.read_file(read_file)
        self.secondary_nodes_ip_list = None
        self.primary_node_ip = None

    def set_nodes_ip_list(self):
        # Get the ip address and the port number
        self.primary = self.config.get('Primary', 'IP')
        self.secondary_nodes_ip_list = self.config.get('Secondary', 'IPs')

#    def __strong_check(self, key, acceptable_latency):
        # can the primary node provide the value within the acceptable latency?

    def put(self, session, key, value):
        # TODO: need to handle errors
        # TODO: This should only go to the main storage node, not the secondaries
        # TODO: provide a timestamp to the put method

        # Get the timestamp
        start = time.time()
        # Make the put call to the server, with [table_name, key, value, timestamp]
        result_status = session.server.put(session.table_name, key, value, start)
        end = time.time()

        # compute the time elapsed between making the call and getting a return value
        elapsed = end-start

        # pass latency information to monitor
        if result_status:
            self.monitor.update_latency(session.ip_address, elapsed)

    def get(self, session, key, sla=None):
        # Need to maintain a timestamp of storage nodes.
        # Timestamps are used to determine if a node can meet the consistency requirements
        # Need to return the value
        if sla is None:
            sla = session.sla

        start = time.time()
        node_return = session.server.get(session.table_name, key)
        end = time.time()
        elapsed = end-start

        # Extract value, timestamp of value, and high-timestamp of the node
        value = node_return['value']
        timestamp = node_return['timestamp']
        high_timestamp = node_return['high_timestamp']

        # TODO: return a condition code that indicates how well the SLA was met, including the consistency of the data
        cc = None

        # TODO: pass information to monitor

        self.monitor.update_latency_and_hightimestamp(session.ip_address, elapsed, high_timestamp)

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
        # TODO: need to deal with possible errors here
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
