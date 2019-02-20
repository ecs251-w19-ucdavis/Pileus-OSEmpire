class SLA:
# Remember, the sla that is used by other classes will actually be a collection of SLAs

    def __init__(self):
        self.consistency = None
        self.latency = None
        self.utility = None

    def set(self, consistency, latency, utility):
        self.consistency = consistency
        self.latency = latency
        self.utility = utility

    def get_consistency(self):
        return self.consistency
        #TODO add error checking if value has not been set before

    def get_latency(self):
        return self.latency
        # TODO add error checking if value has not been set before

    def get_utility(self):
        return self.utility
        # TODO add error checking if value has not been set before