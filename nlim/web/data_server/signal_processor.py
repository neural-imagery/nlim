import asyncio
import json

import numpy as np
import websockets

from nlim.web.data_server.sci import optical_density, scalp_coupling_index

connected_clients: set = set()


async def create_data_processor_client() -> None:
    data_client_endpoint = "ws://127.0.0.1:8080"

    print("Connecting to data client endpoint...")
    async with websockets.connect(data_client_endpoint) as websocket:
        print("Connected to data client endpoint")

        while True:
            device_data: str = await websocket.recv()
            parsed_data: list[list[int]] = json.loads(device_data)
            data_array = np.array(parsed_data).astype("float")

            # data is (C,N), C=32
            od = optical_density(_data=data_array)
            sci = scalp_coupling_index(od)
            listified_sci = sci.tolist()
            signal_quality: str = json.dumps(listified_sci)
            # sci is (C,), sci[i]=sci[i+C/2] for 0<=i<C/2

            print(
                f"Broadcasting signal quality {signal_quality} to {len(connected_clients)} clients"
            )
            for client in connected_clients:
                await client.send(signal_quality)


async def handle_client(websocket, path):
    connected_clients.add(websocket)

    try:
        # Keep the connection open and handle messages
        async for _ in websocket:
            pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)
        print(f"Client disconnected from {path}")


async def main():
    # Configure signal quality server
    host: str = "0.0.0.0"
    port: int = 8081
    server = websockets.serve(handle_client, host, port)

    processor: asyncio.Task = asyncio.create_task(create_data_processor_client())

    print(f"WebSocket server started on ws://{host}:{port}")

    # Run the pipeline
    await asyncio.gather(server, processor)


if __name__ == "__main__":
    asyncio.run(main())
