from Pileus_OSEmpire.src.client.Session import Session
from Pileus_OSEmpire.src.client.SLA import SLA
from Pileus_OSEmpire.src.client.Monitor import Monitor
from Pileus_OSEmpire.src.client.Consistency import Consistency
import time
import configparser

class Client:

    def __init__(self, monitor, config_file_path):
        # An instance of Monitor class, which is updated and queried
        self.monitor = monitor

        # Path to the config file, which provides ip addresses and port numbers
        self.config_file_path = config_file_path

        # An instance of configparser, used to parse the config file
        self.config = configparser.ConfigParser()

        # Read and store the values in the config file
        with open(config_file_path, 'r') as read_file:
            self.config.read_file(read_file)

        # Stores the ip addresses of all secondary nodes available
        self.secondary_nodes_ip_list = self.config.get('Secondary', 'IPs')

        # Stores the ip address of the primary node
        self.primary_node_ip = self.config.get('Primary', 'IP')

        # Store the ip addresses of all the nodes
        self.all_node_ip_list = self.secondary_nodes_ip_list.copy()
        self.all_node_ip_list.append(self.primary_node_ip)

        # Used for all requests to Storage Nodes
        self.session = Session(None, None)

    def set_nodes_ip_list(self):
        # In case some address changes, set it with this function
        self.primary_node_ip = self.config.get('Primary', 'IP')
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

    def put(self, key, value):

        # Get the timestamp
        start = time.time()

        # Make the put call to the server, with [table_name, key, value, timestamp]
        result_status = self.session.storage_node.put(self.session.table_name, key, value, start)

        # Get the end time, for comparison
        end = time.time()

        # compute the time elapsed between making the call and getting a return value
        elapsed = end-start

        # If the put finished correctly
        if result_status:
            # pass latency information to monitor
            self.monitor.update_latency(self.session.ip_address, elapsed)

            # Update the session history information with the key and the timestamp
            self.session.update_put_history(key, start)
        else:
            raise ValueError('Failed to put data on Storage Node.')

    def was_latency_met(self, latency, sla_list):
        # Keep track of the ones that met latency
        latency_met_list = list()

        # Got through all of the SLAs provided and return all whose latency was higher than the given latency
        for sla in sla_list:
            if sla.get_latency() > latency:
                latency_met_list.append(sla)

        return latency_met_list

    def was_consistency_met(self, latency_met_list, node_high_timestamp):
        # Keep track of the ones that met the consistency
        consistency_met_list = list()

        # Go through all of the SLAs provided and return all whose consistency was lower then the given consistency
        for sla in latency_met_list:
            if sla.get_consistency().get_minimum_acceptable_timestamp() < node_high_timestamp:
                consistency_met_list.append(sla)

        return consistency_met_list

    def was_latency_and_consistency_met(self, latency, node_high_timestamp, sla_list):
        # Get the list of SLAs that met the latency
        latency_met_list = self.was_consistency_met(latency, sla_list)

        # Get the list of SLAs that also met the consistency
        consistency_met_list = self.was_consistency_met(latency_met_list, node_high_timestamp)

        return consistency_met_list

    def get(self, key, sla=None):
        # Need to maintain a timestamp of storage nodes.
        # Timestamps are used to determine if a node can meet the consistency requirements
        # Need to return the value

        # There should be a network call either to a single node or to a small set of nodes.

        # If an sla was not provided, use the sla of the session object
        if sla is None:
            sla = self.session.sla

        # Use data from the monitor to figure out the best node.
        # If there are multiple best nodes, choose the closest one.
        # For now, just pick the first out of best_nodes
        target_sla, best_nodes = self.select_target(sla, self.all_node_ip_list, key)

        # Choose the first node out of best nodes
        node_address = best_nodes[0]

        # Connect to the chose node
        self.session.connect_to_server(node_address)

        # Measure the start time for latency calculation
        start = time.time()

        # Make a get request to the connected storage node
        node_return = self.session.storage_node.get(self.session.table_name, key)

        # Calculate the end time
        end = time.time()

        # Calculate the elapsed time
        elapsed = end-start

        # TODO: pass information to monitor
        # If the get returned successfully
        if node_return:
            # Extract value, timestamp of value, and high-timestamp of the node
            value = node_return['value']
            timestamp = node_return['timestamp']
            high_timestamp = node_return['high_timestamp']

            # Pass the information to the monitor
            self.monitor.update_latency_and_hightimestamp(self.session.ip_address, elapsed, high_timestamp)

            # Update the session history information with the key and timestamp
            self.session.update_get_history(key, timestamp)

            # Use the round trip latency, along with the timestamps in the reply to determine which SLAs were met
            slas_met = self.was_latency_and_consistency_met(elapsed, high_timestamp, sla_list)

            return value, slas_met
        else:
            raise ValueError('Failed to make a Get request to server')

    def create_table(self, table_name):
        # check if we have a valid session object
        if self.session is None:
            self.session = Session(table_name, None)
            self.session.connect_to_server()

        # Check if the session is connected
        if self.session.storage_node is None:
            self.session.connect_to_server()

        # Try to create a table
        self.session.storage_node.exposed_create_table(table_name)

    def delete_table(self, table_name):

        # check if we have a valid session object
        if self.session is None:
            self.session = Session(table_name, None)
            self.session.connect_to_server()

        # Check if the session is connected
        if self.session.storage_node is None:
            self.session.connect_to_server()

        # Try to delete the table
        self.session.storage_node.delete_table(table_name)

    def open_table(self, table_name):

        # check if we have a valid session object
        if self.session is None:
            self.session = Session(table_name, None)
            self.session.connect_to_server()

        # Check if the session is connected
        if self.session.storage_node is None:
            self.session.connect_to_server()

        # Try to return the table object
        return self.session.storage_node.get_table(table_name)

    def begin_session(self, table_name, sla):
        # Change the session variable to a new object with the given table name and sla
        self.session = Session(table_name, sla)

        # Connect to the server
        self.session.connect_to_server()

    def end_session(self):
        if self.session is None:
            raise ValueError('Session has already ended.')
        self.session = None


# Implementing session logic
# Needed for read-my-writes, monotonic

if __name__ == "__main__":

    config_file_path = '/home/greghovhannisyan/PycharmProjects/Pileus-OSEmpire/data/Global.conf'

    monitor = Monitor()

    client = Client(monitor, config_file_path)

    #client.create_table('table1')
    #client.create_table('table2')
    #client.delete_table('table2')
    #table = client.open_table('table1')

    #print(table)

    sla1 = SLA(Consistency('strong'), 200, 0.001)
    sla2 = SLA(Consistency('read_my_writes'), 20, 0.0001)
    sla3 = SLA(Consistency('monotonic'), 100, 0.0002)
    sla4 = SLA(Consistency('bounded', time_bound_seconds=10), 5, 0.0004)
    sla5 = SLA(Consistency('causal'), 20, 0.00003)
    sla6 = SLA(Consistency('eventual'), 10, 0.0000001)

    sla_list = [sla1, sla2, sla3, sla4, sla5, sla6]

    # Assume that begin session is called before any put and get operations
    client.begin_session('table1', sla_list)

    client.put('key1', 1)
    client.put('key2', 5)
    client.put('key1', 15)

    client.end_session()




    # sla = []
    # session = Client.begin_session(table, sla)
    #
    # key = 'key1'
    # value = 1
    #
    # Client.put(session, key, value)
    # value, cc = Client.get(session, key)
    #
    # Client.end_session(session)
