# Monitoring storage nodes

import configparser
import time
import rpyc
from Pileus_OSEmpire.src.client.Consistency import Consistency

class Monitor:

    def __init__(self):
        # This will store latency and high_timestamp information for all nodes
        self.node_dictionary = dict()

        # Parse configuration
        # Get the config file
        self.config = configparser.ConfigParser()
        self.config.read_file(open('../../data/Global.conf'))

        # Stores the ip addresses of all secondary nodes available
        self.secondary_nodes_ip_list = self.config.get('Secondary', 'IPs').split(',')
        # Stores the ip address of the primary node
        self.primary_node_ip = self.config.get('Primary', 'IP')

        # Store the ip addresses of all the nodes
        self.all_node_ip_list = self.secondary_nodes_ip_list.copy()
        self.all_node_ip_list.append(self.primary_node_ip)

        # Only consider the last window_size latency entries
        self.window_size = 10

        # Timeout for sending active probes 100 ms
        self.timeout = 100 

    # This function will be called by the client after a Put call
    def update_latency(self, node_identifier, latency):
        # If the latency value is already a list, then add to it
        if node_identifier in self.node_dictionary.keys():
            # Only keep the last sliding windows size latencies
            if len(self.node_dictionary[node_identifier]['latency']) < self.window_size:
                self.node_dictionary[node_identifier]['latency'].append(latency)
            else:
                self.node_dictionary[node_identifier]['latency'].pop(0)
                self.node_dictionary[node_identifier]['latency'].append(latency)
        else:
            # If this is a new key, add a list under the latency key and add the new latency value to the list
            self.node_dictionary[node_identifier] = dict()
            self.node_dictionary[node_identifier]['latency'] = list()
            self.node_dictionary[node_identifier]['latency'].append(latency)

    def update_high_timestamp(self, node_identifier, high_timestamp):
        self.node_dictionary[node_identifier]['high_timestamp'] = high_timestamp

    # This will be called by the client after a Get call
    def update_latency_and_hightimestamp(self, node_identifier, latency, high_timestamp):

        self.update_latency(node_identifier, latency)

        self.update_high_timestamp(node_identifier, high_timestamp)

        self.node_dictionary[node_identifier]['last_accessed'] = time.time()

    def send_probe(self):
        port_number = int(self.config.get('GeneralConfiguration', 'ClientServerPort'))

        for node_identifier in self.all_node_ip_list:
            start = time.time()
            print(node_identifier)
            print(port_number)
            high_timetsamp = rpyc.connect(node_identifier, port_number).root.get_probe()
            end = time.time()

            # Update the high_timestamp of this node
            self.update_latency_and_hightimestamp(node_identifier, end-start, high_timetsamp)

    # Send active probes
    def send_active_probes(self):
        now = time.time()

        # Get port number
        port_number = int(self.config.get('GeneralConfiguration', 'ClientServerPort'))

        # For each node, send active probes if idle for timeout
        for node_identifier in self.node_dictionary.keys():

            #high_ts = self.node_dictionary[node_identifier]['high_timestamp']

            past_time = now - self.timeout

            if past_time > self.node_dictionary[node_identifier]['last_accessed']:

                start = time.time()

                s = rpyc.connect(node_identifier, port=port_number)
                c = s.root
                c.get_probe()

                end = time.time()

                elapsed = end-start

                self.update_latency(node_identifier, elapsed)

                self.node_dictionary[node_identifier]['last_accessed'] = time.time()

    def p_node_cons(self, node_identifier, consistency, key):

        # Get the high timestamp of the given key
        node_high_timestamp = self.node_dictionary[node_identifier]['high_timestamp']

        minimum_acceptable_timestamp = consistency.get_minimum_acceptable_timestamp()

        # Strong consistency: send directly to the primary
        if consistency == Consistency.STRONG:
            if node_identifier == self.config.get('Primary', 'IP'):
                return 1
            else:
                return 0

        if node_high_timestamp >= minimum_acceptable_timestamp:
            return 1
        else:
            return 0

    # Function to calculate an estimate of the probablity that the node can respond to Gets within the given reponse time 
    def p_node_lat(self, node_identifier, desired_latency):
        # TODO: add check if information on this node is not available
        # Go through the latencies for this node and compute how many are less than desired latency

        # Counts how many are below the desired latency
        counter = 0.0
        
        # Global counter to avoid cold start problem
        total = 0.0

        for latency in self.node_dictionary[node_identifier]['latency']:
            total += 1
            if latency < desired_latency:
                counter += 1

        return counter / total

    def p_node_sla(self, node_identifier, consistency, desired_latency, key):
        # TODO: error handling !!

        cons = self.p_node_cons(node_identifier, consistency, key)

        lat = self.p_node_lat(node_identifier, desired_latency)

        return lat * cons

if __name__ == "__main__":

    monitor = Monitor()
    monitor.send_active_probes()