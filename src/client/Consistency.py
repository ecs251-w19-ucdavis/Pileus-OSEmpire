class Consistency:
    # provides a consistent api for getting values from different consistency levels
    STRONG = 'strong'
    EVENTUAL = 'eventual'
    READ_MY_WRITES = 'read_my_writes'
    MONOTONIC = 'monotonic'
    BOUNDED = 'bounded'
    CAUSAL = 'causal'

    def __init__(self, type_str, time_bound_seconds=None):
        # If the type provided is not one that we know of, throw an error
        if type_str not in [Consistency.STRONG,
                            Consistency.EVENTUAL,
                            Consistency.READ_MY_WRITES,
                            Consistency.MONOTONIC,
                            Consistency.BOUNDED,
                            Consistency.CAUSAL]:
            raise ValueError('not an acceptable type of consistency')
        self.type_str = type_str

        # This is used only for bounded consistency, should be None for all other types
        self.time_bound = time_bound_seconds

        # This value will be updated by client or session and used by monitor.
        self.minimum_acceptable_timestamp = None

    def set_minimum_acceptable_timestamp(self, timestamp):
        self.minimum_acceptable_timestamp = timestamp

    def get_minimum_acceptable_timestamp(self):
        if self.minimum_acceptable_timestamp is None:
            raise ValueError('The minimum acceptable timestamp has not been set: ' + self.type_str)
        else:
            return self.minimum_acceptable_timestamp


if __name__ == "__main__":
    strong = Consistency(Consistency.STRONG)
    eventual = Consistency(Consistency.EVENTUAL)
    read_my_writes = Consistency(Consistency.READ_MY_WRITES)
    monotonic = Consistency(Consistency.MONOTONIC)
    bounded = Consistency(Consistency.BOUNDED, time_bound_seconds=10)
    causal = Consistency(Consistency.CAUSAL)

    consistency_list = [strong, eventual, read_my_writes, monotonic, bounded, causal]

    for con in consistency_list:
        print(con.type_str)
        print(con.time_bound)
        con.set_minimum_acceptable_timestamp(100)
        print(con.get_minimum_acceptable_timestamp())

    wrong = Consistency('dslkfhiosdj')
