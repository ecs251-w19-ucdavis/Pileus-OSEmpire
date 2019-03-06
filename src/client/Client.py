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

    def select_target(self, sla_list, node_list, key):
        # This will be updated to keep track of which sla provides the highest utility
        max_util = -1

        # Add the best nodes to this list
        best_nodes = list()

        # Initialize with some large value for now, will be updated later
        best_latency = 1000

        # This will eventually contain the best sla and be returned
        target_sla = None

        # Loop through all of the SLAs
        for sub_sla in sla_list:
            # Loop through all of the known nodes. Should this include the primary?
            for node in node_list:
                # Compute the predicted utility for this node, given this sla
                util = self.monitor.p_node_sla(node, sub_sla.consistency, sub_sla.latency, key) * sub_sla.utility

                # If this has the highest utility seen so far
                if util > max_util:
                    # Update this as the sla we are looking for
                    target_sla = sub_sla

                    # Update the new maximum utility that we will try to beat
                    max_util = util

                    # Clear the previous best nodes, if any. Add only this new node to the list
                    best_nodes.clear()
                    best_nodes.append(node)

                # If there was another node with the equivalent utility, add it to the list, along with the other ones.
                elif util == max_util:
                    best_nodes.append(node)

        # Now go through all of the best nodes and choose by latency
        for node in best_nodes:
            if node.latency < best_latency:
                best_nodes = node
                best_latency = node.latency

        # TODO: add some corner case handling, if all of the best nodes have the same latency

        return target_sla, best_nodes

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

        # If the put finished correctly
        if result_status:
            # pass latency information to monitor
            self.monitor.update_latency(session.ip_address, elapsed)

            # Update the session history information with the key and the timestamp
            session.update_put_history(key, start)
        else:
            pass
            # TODO: need some way to handle the put class not working

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

        # TODO: pass information to monitor
        # If the get returned successfully
        if node_return:
            # Extract value, timestamp of value, and high-timestamp of the node
            value = node_return['value']
            timestamp = node_return['timestamp']
            high_timestamp = node_return['high_timestamp']

            # Pass the information to the monitor
            self.monitor.update_latency_and_hightimestamp(session.ip_address, elapsed, high_timestamp)

            # Update the session history information with the key and timestamp
            session.update_get_history(key, timestamp)
        else:
            # TODO: properly handle the case when Get fails
            pass


        # TODO: return a condition code that indicates how well the SLA was met, including the consistency of the data
        cc = None

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
