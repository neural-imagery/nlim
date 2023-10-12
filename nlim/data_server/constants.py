import os

PLATFORM_PORT: int = int(os.environ.get("PLATFORM_PORT", "9001"))
PLATFORM_HOST: str = os.environ.get("PLATFORM_HOST", "127.0.0.1")

DEVICE_DATA_PORT: int = int(os.environ.get("DEVICE_DATA_PORT", "9000"))
DEVICE_DATA_HOST: str = os.environ.get("DEVICE_DATA_HOST", "127.0.0.1")
