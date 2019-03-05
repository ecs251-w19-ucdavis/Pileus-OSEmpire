# Monitoring storage nodes

import configparser

class Monitor:

    def __init__(self):
        # This will store latency and high_timestamp information for all nodes
        self.node_dictionary = dict()

        # Parse configuration
        self.config = configparser.ConfigParser()

        # Only consider the last window_size latency entries
        self.window_size = 10

    # This function will be called by the client after a Put call
    def update_latency(self, node_identifier, latency):
        # If the latency value is already a list, then add to it
        if node_identifier in self.node_dictionary[node_identifier].keys():
            # Only keep the last sliding windows size latencies
            if len(self.node_dictionary[node_identifier]['latency']) < self.window_size:
                self.node_dictionary[node_identifier]['latency'].append(latency)
            else:
                self.node_dictionary[node_identifier]['latency'].pop(0)
                self.node_dictionary[node_identifier]['latency'].append(latency)
        else:
            # If this is a new key, add a list under the latency key and add the new latency value to the list
            self.node_dictionary[node_identifier]['latency'] = list()
            self.node_dictionary[node_identifier]['latency'].append(latency)

    # This will be called by the client after a Get call
    def update_latency_and_hightimestamp(self, node_identifier, latency, high_timestamp):

        self.node_dictionary[node_identifier]['high_timestamp'] = high_timestamp

        self.update_latency(node_identifier, latency)

    def p_node_cons(self, node_identifier, consistency, key):

        # Get the high timestamp of the given key
        node_high_timestamp = self.node_dictionary[node_identifier]['high_timestamp']

        # TODO: find some way to provide a minimum acceptable time_stamp for a given consistency
        minimum_acceptable_timestamp = consistency.timestamp

        # Strong consistency: send directly to the primary
        if consistency == 'strong': 
            if node_identifier == self.config.get('Primary', 'IP'):
                return 1
            else:
                return 0

        # Read-my-writes: the maximum timestamp of any previous puts to the key being acessed in the current Get
        elif consistency == 'read_my_writes':
            pass

        # Monotonic: the recorded timestamp for the key being accessed in the Get
        elif consistency == 'monotonic':
            pass
        
        # Bounded: the current time minus the desired time bound 
        elif consistency == 'bounded':
            pass

        # Causual : the maximum timestamp of any object that previously read or written in this session
        elif consistency == 'causal':
            pass
        
        # Eventual: minimum acceptable timestamp is zero
        else:
            minimum_acceptable_timestamp = 0

        if node_high_timestamp > minimum_acceptable_timestamp:
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

