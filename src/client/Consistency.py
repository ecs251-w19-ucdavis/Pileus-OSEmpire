class Consistency:
    # provides a consistent api for getting values from different consistency levels

    def __init__(self, type_str, time_bound_seconds=None):
        # If the type provided is not one that we know of, throw an error
        if type_str not in ['strong', 'eventual', 'read_my_writes', 'monotonic', 'bounded', 'causal']:
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
            raise ValueError('The minimum acceptable timestamp has not been set')
