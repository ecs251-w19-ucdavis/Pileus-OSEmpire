import configparser
import rpyc

class Session:

    def __init__(self, table_name, sla):
        self.table_name = table_name
        self.sla = sla
        self.server = None
        self.ip_address = None
        # TODO: add the ip address of the server connected to

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