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

    data_to_send = json.dumps({"data": "Hello, TCP/IP Server!"}).encode("utf-8")

    # Send the data
    sock.send(data_to_send)

    # Optionally, receive a response from the server
    response = sock.recv(1024)  # Receive up to 1024 bytes

    print("Sent:", data_to_send)
    print("Received:", response.decode("utf-8"))  # Assuming the response is a string
except Exception as e:
    print("Error:", e)
finally:
    # Close the socket
    sock.close()