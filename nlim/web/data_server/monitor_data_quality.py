import asyncio

import websockets


async def monitor_socket():
    uri = "ws://localhost:8081"  # Replace with the WebSocket server URI

    async with websockets.connect(uri) as websocket:
        while True:
            try:
                message = await websocket.recv()
                print(f"Received: {message}")
            except websockets.exceptions.ConnectionClosed:
                print("Socket connection closed.")
                break


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(monitor_socket())
