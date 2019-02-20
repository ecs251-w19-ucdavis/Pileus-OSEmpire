import configparser
import rpyc

class Session:

    def __init__(self, table_name, sla):
        self.table_name = table_name
        self.sla = sla

    def connect_to_server(self):
        config = configparser.ConfigParser()
        config.read_file(open('../../data/Global.conf'))

        # Get the ip address and the port number
        ip = config.get('Primary', 'IP')
        port = config.get('GeneralConfiguration', 'ClientServerPort')

        # Get the connection object
        connection = rpyc.connect(ip, port=port)

        return connection.root


if __name__ == "__main__":

    session = Session('bob', list())

    session.connect_to_server()

    #server.get('1')
    #server.put(...)