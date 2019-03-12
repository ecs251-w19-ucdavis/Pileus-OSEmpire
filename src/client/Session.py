import configparser
import rpyc
from Pileus_OSEmpire.src.client.Consistency import Consistency
from Pileus_OSEmpire.src.client.SLA import SLA
import time


class Session:

    def __init__(self, table_name, sla):
        # The name of the table that we will operate on
        # This is a string for now.
        self.table_name = table_name

        # a list of type SLA
        self.sla = sla

        # A connection to a StorageNode through rpyc
        self.storage_node = None

        # The ip address of the StorageNode that this session is connected to
        self.ip_address = None

        # Keeps track of and updates latest timestamp of each key, which was involved in a put call
        self.put_history = dict()

        # Keeps track of and updates latest timestamp of each key, which was involved in a get call
        self.get_history = dict()

        # Stores the periodically updated timestamp of the key with the highest timestamp, both in puts and gets
        self.maximum_timestamp = 0

    def update_consistency(self, consistency, key):
        # For now, we will have a special case for strong. The monitor will always return true for the primary node
        # TODO: look into a way to send requests for non-primary nodes, though this is outside of paper scope
        if consistency.type_str == Consistency.STRONG:
            consistency.set_minimum_acceptable_timestamp(None)

        # Maximum timestamp of any previous Puts to the key being accessed
        elif consistency.type_str == Consistency.READ_MY_WRITES:
            consistency.set_minimum_acceptable_timestamp(self.put_history[key])

        # Latest timestamp of previous Gets for given key
        elif consistency.type_str == Consistency.MONOTONIC:
            consistency.set_minimum_acceptable_timestamp(self.get_history[key])

        # current time minus the desired bound time
        elif consistency.type_str == Consistency.BOUNDED:
            consistency.set_minimum_acceptable_timestamp(time.time() - consistency.time_bound_seconds)

        # Maximum timestamp of any object that was read or written in this session
        elif consistency.type_str == Consistency.CAUSAL:
            consistency.set_minimum_acceptable_timestamp(self.maximum_timestamp)

        # Simply set to zero
        elif consistency.type_str == Consistency.EVENTUAL:
            consistency.set_minimum_acceptable_timestamp(0)

        # This should never happen
        else:
            raise ValueError('Somehow we have a consistency that is not in consistency class.')

    def update_all_consistencies(self, key):
        for sla in self.sla:
            self.update_consistency(sla.consistency, key)

    def connect_to_server(self, address=None):
        # Get the config file
        config = configparser.ConfigParser()
        config.read_file(open('../../data/Global.conf'))

        # Get the port
        port = int(config.get('GeneralConfiguration', 'ClientServerPort'))

        # If no address was provided, then use the default
        if address is None:
            # Get the ip address and the port number
            address = config.get('Primary', 'IP')

        # Update the address variable
        self.ip_address = address

        # Get the connection object
        connection = rpyc.connect(self.ip_address, port=port)

        # Update the storage node variable, which will be used to make the calls
        self.storage_node = connection.root

        return connection.root

    def update_maximum_timestamp(self, timestamp):
        # This should always be called on successful Puts
        # This might not be called on all successful Gets
        if timestamp > self.maximum_timestamp:
            self.maximum_timestamp = timestamp

    def update_put_history(self, key, timestamp):
        self.put_history[key] = timestamp

        # Need to update the maximum timestamp
        self.update_maximum_timestamp(timestamp)

        # Update consistency minimums
        self.update_all_consistencies(key)

    def update_get_history(self, key, timestamp):
        self.get_history[key] = timestamp

        # Need to update the maximum timestamp
        self.update_maximum_timestamp(timestamp)

        # Update consistency minimums
        self.update_all_consistencies(key)

    def disconnect(self):
        # Not really sure how this works.
        self.storage_node = None


if __name__ == "__main__":

    sla1 = SLA(Consistency('strong'), 200, 0.001)
    sla2 = SLA(Consistency('read_my_writes'), 20, 0.0001)
    sla3 = SLA(Consistency('monotonic'), 100, 0.0002)
    sla4 = SLA(Consistency('bounded', time_bound_seconds=10), 5, 0.0004)
    sla5 = SLA(Consistency('causal'), 20, 0.00003)
    sla6 = SLA(Consistency('eventual'), 10, 0.0000001)

    sla_list = [sla1, sla2, sla3, sla4, sla5, sla6]

    session = Session('table1', sla_list)

    session.connect_to_server()

    for i in range(10):
        session.update_get_history('key' + str(i), 10 + i)
        session.update_put_history('key' + str(i), 10 + i)

    print(session.put_history)
    print(session.get_history)
    print(session.maximum_timestamp)
