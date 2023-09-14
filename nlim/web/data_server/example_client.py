import http.server
import socketserver

# Set the port number
port = 8080

# Change to the desired directory
directory = "."  # By default, it serves the current directory

# Create the server handler
handler = http.server.SimpleHTTPRequestHandler

# Run the server
with socketserver.TCPServer(("", port), handler) as httpd:
    print(f"Serving at port {port}")
    httpd.serve_forever()
