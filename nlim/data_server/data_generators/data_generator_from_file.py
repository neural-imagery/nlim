import json
import socket
import time

from scipy.io import loadmat

# Define the target host and port
host = "127.0.0.1"
port = 9000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to the server
    sock.connect((host, port))

    nirs_data: dict = loadmat("./scan.nirs")
    # List of channel readouts at each timestep
    channel_readouts: list[list[int]] = nirs_data["d"]
    row_idx: int = 0

    while True:
        data_to_send = json.dumps({"d": [{"data": channel_readouts[row_idx].tolist()}]})
        data_to_send = f"{len(data_to_send)} {data_to_send}"
        data_to_send = data_to_send.encode("utf-8")

        sock.send(data_to_send)
        print("Sent:", data_to_send)

        time.sleep(0.1)

        row_idx += 1
        if row_idx == len(channel_readouts):
            row_idx = 0

except Exception as e:
    print("Error:", e)
finally:
    sock.close()
