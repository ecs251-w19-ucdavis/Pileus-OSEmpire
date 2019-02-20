from ..client.Session import Session
from ..client.SLA import SLA

class Client:

    def __init__(self):
        self.session = None

    @staticmethod
    def put(key, value):

    @staticmethod
    def get(key, sla=None):
        # Need to maintain a timestamp of storage nodes.
        # Timestamps are used to determine if a node can meet the consistency requirements
        # Need to return the value
        if sla is None:
            sla = self.session.sla


    def create_table(self, name):



    def delete_table(self, name):



    def open_table(self, name):
        # Return some table object

    def begin_session(self, table_name, sla):
        # Returns some session object
        return Session(table_name, sla)

    def end_session(self, session_object):
        # ends the connection to the table and flushes data




# Implementing session logic
# Needed for read-my-writes, monotonic,