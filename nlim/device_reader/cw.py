import json
from typing import Generator

import numpy as np
import serial
from websockets.sync import client

# Send it via websocket to the server
device_data_endpoint_client = client.connect("ws://127.0.0.1:9001/device_data/source")


def read_serial(com_port_name: str, baud_rate: int) -> Generator[float, None, None]:
    ser = serial.Serial(com_port_name, baud_rate, timeout=None)

    arr = np.zeros(100)
    buffer_size: int = 0
    while True:
        data: float = ser.readline().decode()
        arr[buffer_size] = data

        if buffer_size >= arr.shape[0]:
            # TODO(spolcyn): I have quite some concerns about this being too slow to
            # get data off the serial fast enough, esp. given the extra processing
            # requirements to put together the encoded JSON string, which is quite
            # extensive and unnecessarily complicated
            device_data_endpoint_client.send(
                json.dumps({"d": [{"data": arr.tolist()}]}).encode("utf-8")
            )


# Reads device data for the continuous wave system

# Read from the serial port what the arduino is sending
