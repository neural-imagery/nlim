import json
from collections import deque
from typing import Deque

from nlim.data_server.processors.processor import Processor

num_channels: int = 32


class DeviceDataProcessor(Processor):
    def __init__(self, window_size: int = 128):
        self.window_size = window_size
        self.rolling_window: list[Deque[int]] = [
            deque(maxlen=window_size) for _ in range(num_channels)
        ]

    def process_new_data(self, channel_data: list[int]) -> str:
        for index, val in enumerate(channel_data):
            self.rolling_window[index].append(val)

        return json.dumps([list(window) for window in self.rolling_window])
