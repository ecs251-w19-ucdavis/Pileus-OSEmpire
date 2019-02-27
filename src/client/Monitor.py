# Record the set of nodes for each

class Monitor:


    def __init__(self):
        # This will store latency and high_timestamp information for all nodes
        # TODO: This should only hold information on some recent data, not all. Please modify as needed
        self.node_dictionary = dict()

        # only consider the last window_size latency entries.
        self.window_size = 10.0

    # This will be called by the client after a Put call
    def update_latency(self, node_identifier, latency):
        # If the latency value is already a list, then add to it
        if node_identifier in self.node_dictionary[node_identifier].keys():
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

        if node_identifier > minimum_acceptable_timestamp:
            return 1
        else:
            return 0

    def p_node_lat(self, node_identifier, desired_latency):
        # TODO: add check if information on this node is not available
        # Go through the latencies for this node and compute how many are less than desired latency

        # Counts how many are below the desired latency
        counter = 0.0

        for latency in self.node_dictionary[node_identifier]['latency']:
            if latency < desired_latency:
                counter += 1

        return counter / self.window_size

    def p_node_sla(self, node_identifier, consistency, desired_latency, key):
        # TODO: error handling !!

        cons = self.p_node_cons(node_identifier, consistency, key)

        lat = self.p_node_lat(node_identifier, desired_latency)

        return lat * cons








