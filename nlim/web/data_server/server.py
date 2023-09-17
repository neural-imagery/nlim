import asyncio
import json
import logging
import os
from collections import defaultdict
from typing import DefaultDict

import websockets

from nlim.web.data_server.processors.device_data_processor import DeviceDataProcessor
from nlim.web.data_server.processors.processor import Processor
from nlim.web.data_server.processors.signal_processor import SignalQualityProcessor

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO").upper())
logger = logging.getLogger(__name__)

path_to_clients: DefaultDict[str, set] = defaultdict(set)
path_to_processor: dict[str, Processor] = {
    "/signal_quality": SignalQualityProcessor(),
    "/device_data": DeviceDataProcessor(),
}


def broadcast_device_data(device_data: list[int]):
    path_to_result: dict[str, str] = {
        path: processor.process_new_data(device_data)
        for path, processor in path_to_processor.items()
        if path != "/device_data/source"
    }

    for path, result in path_to_result.items():
        logger.info(f"[{path}] Broadcasting result")
        clients = path_to_clients[path]
        websockets.broadcast(clients, result)


async def handle_client(websocket, path):
    logger.info(f"Connected new client on {path}")
    path_to_clients[path].add(websocket)

    try:
        # Keep the connection open and handle messages
        async for message in websocket:
            if path == "/device_data/source":
                # broadcast to all other clients
                device_data: list[int] = json.loads(message)
                broadcast_device_data(device_data)
            else:
                pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        path_to_clients[path].remove(websocket)
        logger.info(f"Client disconnected from {path}")


async def main():
    # Run the pipeline
    stop = asyncio.Future()
    PORT = 9001
    server = await websockets.serve(handle_client, "0.0.0.0", PORT)
    logger.info(f"Running platform on port {PORT}")
    await stop


if __name__ == "__main__":
    asyncio.run(main())
