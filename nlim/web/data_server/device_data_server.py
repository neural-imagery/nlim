import json
import logging
import os
import socket
from typing import Union, cast

from websockets.sync import client

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO").upper())
logger = logging.getLogger(__name__)

device_data_endpoint_client = client.connect("ws://127.0.0.1:9001/device_data/source")
data_endpoint = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Matlab indices to re-sort the array -- index 1 (old) goes to index 1 (new),
# index 2 (old) goes to index 3 (new), and so on
# Maps (index in input array -> index in output array)
channel_to_index: list[int] = [
    1,
    3,
    5,
    7,
    9,
    11,
    13,
    15,
    17,
    19,
    21,
    23,
    25,
    27,
    29,
    31,
    2,
    4,
    6,
    8,
    10,
    12,
    14,
    16,
    18,
    20,
    22,
    24,
    26,
    28,
    30,
    32,
]
channel_to_index = [val - 1 for val in channel_to_index]  # 0-index
logger.info(f"channel to index {channel_to_index}")


def handle_connection(client_socket, client_address: str):
    logger.info(f"Got connection {client_socket}, {client_address}")
    message_length: int = -1
    message_buffer: bytearray = bytearray()

    while True:
        data: bytes = client_socket.recv(4096)
        if not data:
            break

        if message_length == -1:
            space_char_code: int = 32
            separator_index: int = data.find(bytes([space_char_code]))
            message_length = int(data[:separator_index].decode("utf-8"))
            logger.info(f"Stated message length is {message_length}")

            data = data[separator_index + 1 :]
            logger.debug(f"Received data {data.decode('utf-8')}")

        message_buffer.extend(data)

        if len(message_buffer) >= message_length:
            logger.debug("Time to send message")
            # Expected format:
            # {"d": [{"data": [...ints...]} * timestemps]}
            # But if there's only one "data": dict, then there will be no list
            try:
                decoded_data: dict = json.loads(message_buffer.decode("utf-8"))

                data_dicts: Union[list, list[dict]] = decoded_data.get("d", [])
                if isinstance(data_dicts, dict):
                    data_dicts = [data_dicts]
                data_dicts = cast(list[dict], data_dicts)

                assert isinstance(data_dicts, list)
                for data_dict in data_dicts:
                    assert isinstance(data_dict, dict)
                    if "data" not in data_dict:
                        continue

                    channel_data: list[int] = data_dict["data"]
                    reordered_data: list[int] = [
                        channel_data[idx] for idx in channel_to_index
                    ]
                    device_data_endpoint_client.send(json.dumps(reordered_data))
            except json.decoder.JSONDecodeError:
                logger.exception("Buffer contents: %s", message_buffer.decode("utf-8"))
            finally:
                message_buffer = bytearray()
                message_length = -1


data_endpoint.bind(("0.0.0.0", 9000))
data_endpoint.listen(5)
logger.info("Server is listening on port 9000")

while True:
    client_socket, client_address = data_endpoint.accept()
    handle_connection(client_socket, client_address)
