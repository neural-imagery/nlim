import json
from collections import deque
from typing import Deque

import numpy as np

from nlim.data_server.processors.processor import Processor
from nlim.data_server.sci import optical_density, scalp_coupling_index

num_channels: int = 32


class SignalQualityProcessor(Processor):
    def __init__(self, window_size: int = 128):
        self.window_size = window_size
        self.rolling_window: list[Deque[int]] = [
            deque(maxlen=window_size) for _ in range(num_channels)
        ]

    def process_new_data(self, channel_data: list[int]) -> str:
        for index, val in enumerate(channel_data):
            self.rolling_window[index].append(val)

        data_array = np.array([list(window) for window in self.rolling_window]).astype(
            "float"
        )

        # data is (C,N), C=32
        od = optical_density(_data=data_array)
        sci = scalp_coupling_index(od)
        listified_sci = sci.tolist()
        signal_quality: str = json.dumps(listified_sci)
        # sci is (C,), sci[i]=sci[i+C/2] for 0<=i<C/2

        return signal_quality
