from ..client.Consistency import Consistency

class SLA:
# Remember, the sla that is used by other classes will actually be a collection of SLAs

    def __init__(self, consistency=None, latency=None, utility=None):
        self.consistency = consistency
        self.latency = latency
        self.utility = utility

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


if __name__ == "__main__":
    sla1 = SLA(Consistency('strong'), 200, 0.00001)
    sla1 = SLA(Consistency('read_my_writes'), 200, 0.00001)
    sla1 = SLA(Consistency('monotonic'), 200, 0.00001)
    sla1 = SLA(Consistency('bounded', time_bound_seconds=10), 200, 0.00001)
    sla1 = SLA(Consistency('causal'), 200, 0.00001)
    sla1 = SLA(Consistency('eventual'), 200, 0.00001)