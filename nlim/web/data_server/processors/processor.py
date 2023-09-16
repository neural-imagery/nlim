import abc


class Processor:
    def __init__(self):
        pass

    @abc.abstractmethod
    def process_new_data(self, channel_data: list[int]) -> str:
        """
        Process single timestep of data from the channel and return a
        JSON-encoded string with the result of this processor
        """
        raise NotImplementedError
