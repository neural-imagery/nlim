import random
import socket

# Define the target host and port
host = "127.0.0.1"
port = 9000

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to the server
    sock.connect((host, port))

    # Data to send (as bytes)
    import json
    import time

    # Mimics the form of data received from our TechEn backend
    while True:
        data = [random.randint(0, 100) for _ in range(32)]
        noise = [random.randint(0, 100) for _ in range(600)]
        data_to_send = json.dumps({"d": [{"data": data} for _ in range(5)]})
        data_to_send = f"{len(data_to_send)} {data_to_send}"
        data_to_send = data_to_send.encode("utf-8")

        # Send the data
        sock.send(data_to_send)

        print("Sent:", data_to_send)
        time.sleep(2)

except Exception as e:
    print("Error:", e)
finally:
    sock.close()
