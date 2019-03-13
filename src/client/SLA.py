import Consistency

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
        if self.consistency is None:
            raise ValueError('the consistency has not been set.')
        else:
            return self.consistency

    def get_latency(self):
        if self.consistency is None:
            raise ValueError('the latency has not been set.')
        else:
            return self.latency

    def get_utility(self):
        if self.consistency is None:
            raise ValueError('the utility has not been set.')
        else:
            return self.utility


if __name__ == "__main__":
    sla1 = SLA(Consistency('strong'), 200, 0.001)
    sla2 = SLA(Consistency('read_my_writes'), 20, 0.0001)
    sla3 = SLA(Consistency('monotonic'), 100, 0.0002)
    sla4 = SLA(Consistency('bounded', time_bound_seconds=10), 5, 0.0004)
    sla5 = SLA(Consistency('causal'), 20, 0.00003)
    sla6 = SLA(Consistency('eventual'), 10, 0.0000001)

    sla_list = [sla1, sla2, sla3, sla4, sla5, sla6]

    for sla in sla_list:
        print(sla.get_consistency().type_str)
        print(sla.get_latency())
        print(sla.get_utility())
