import json
import random
import socket
import time

from nlim.data_server.constants import DEVICE_DATA_HOST, DEVICE_DATA_PORT
from nlim.util import get_logger

logger = get_logger()

address: tuple[str, int] = (DEVICE_DATA_HOST, DEVICE_DATA_PORT)

# Connect to the server
device_data_server_client = None
while device_data_server_client is None:
    try:
        device_data_server_client = socket.create_connection(
            address=address, timeout=10
        )
    except ConnectionError:
        logger.exception("Error while connecting to device data server")
        time.sleep(2)

try:
    # Mimics the form of data received from our TechEn backend
    while True:
        data = [random.randint(0, 100) for _ in range(32)]
        noise = [random.randint(0, 100) for _ in range(600)]
        data_to_send = json.dumps({"d": [{"data": data} for _ in range(5)]})
        data_to_send = f"{len(data_to_send)} {data_to_send}"
        data_to_send = data_to_send.encode("utf-8")

        # Send the data
        device_data_server_client.send(data_to_send)

        print("Sent:", data_to_send)
        time.sleep(2)

except Exception as e:
    print("Error:", e)
finally:
    device_data_server_client.close()
