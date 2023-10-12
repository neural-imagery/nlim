import json
import socket
import time
from pathlib import Path

from scipy.io import loadmat

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

# Load the data file
nirs_file: Path = Path(__file__).parent / "scan.nirs"
nirs_data: dict = loadmat(str(nirs_file.absolute()))

# Get the list of channel readouts at each timestep
channel_readouts: list[list[int]] = nirs_data["d"]
row_idx: int = 0

try:
    while True:
        data_to_send = json.dumps({"d": [{"data": channel_readouts[row_idx].tolist()}]})
        data_to_send = f"{len(data_to_send)} {data_to_send}"
        data_to_send = data_to_send.encode("utf-8")

        device_data_server_client.send(data_to_send)
        print("Sent:", data_to_send)

        time.sleep(0.1)

        row_idx += 1
        if row_idx == len(channel_readouts):
            row_idx = 0

except Exception as e:
    logger.exception(f"Error with connection/data sending, address {address}")
finally:
    device_data_server_client.close()
