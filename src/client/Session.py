import configparser
import rpyc
from ..client.Consistency import Consistency
import time

class Session:

    def __init__(self, table_name, sla):
        self.table_name = table_name
        self.sla = sla
        self.server = None
        self.ip_address = None

        # Keeps track of and updates latest timestamp of each key, which was involved in a put call
        self.put_history = dict()

        # Keeps track of and updates latest timestamp of each key, which was involved in a get call
        self.get_history = dict()
        # TODO: add the ip address of the server connected to

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


    def connect_to_server(self):
        config = configparser.ConfigParser()
        config.read_file(open('../../data/Global.conf'))

        # Get the ip address and the port number
        ip = config.get('Primary', 'IP')

        self.id_address = ip

        port = int(config.get('GeneralConfiguration', 'ClientServerPort'))

        # Get the connection object
        connection = rpyc.connect(ip, port=port)

        self.server = connection.root

        return connection.root

    def disconnect(self):
        # Not really sure how this works.
        self.connection = None


if __name__ == "__main__":

    session = Session('bob', list())

    session.connect_to_server()

    #server.get('1')
    #server.put(...)