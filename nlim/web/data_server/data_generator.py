import random
import socket

# Define the target host and port
host = "127.0.0.1"  # Replace with the target hostname or IP address
port = 9000  # Replace with the target port number

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to the server
    sock.connect((host, port))

    # Data to send (as bytes)
    import json
    import time

    while True:
        with open('data1.json', 'r') as f:
            dict = json.load(f)
        clean = dict['sig']
        noisy = dict['noise']
        data = [float(x) + random.randint(0, 50) for x in clean]
        # data = [random.randint(0, 100) for _ in range(600)]
        noise = [float(x) + random.randint(0, 50) for x in noisy]
        # noise = [random.randint(0, 100) for _ in range(600)]
        data_to_send = json.dumps({"d": [{"data": data, "noise": noise}]})
        data_to_send = f"{len(data_to_send)} {data_to_send}"
        data_to_send = data_to_send.encode("utf-8")

        # Send the data
        sock.send(data_to_send)

        # Optionally, receive a response from the server
        # response = sock.recv(1024)  # Receive up to 1024 bytes
        response = b""

        print("Sent:", data_to_send)
        print(
            "Received:", response.decode("utf-8")
        )  # Assuming the response is a string
        time.sleep(2)

except Exception as e:
    print("Error:", e)
finally:
    # Close the socket
    sock.close()